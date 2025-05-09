from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse

from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.db_schemes import DataChunk, Asset
from models import AssetTypeEnums
import os
import aiofiles
import logging

from .schemes.data import ProcessRequest, DeleteRequest
from controllers import VectorDBController

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix='/api/v1/data',
    tags=['api_v1_data']
)

@data_router.post('/upload/{project_id}')
async def upload_data(request: Request, project_id: int, file: UploadFile, app_settings: Settings = Depends(get_settings)):


    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)
    
    # Validation the file properties.
    data_controller = DataController()
    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)
    
    if not is_valid:
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {
                'signal': result_signal
            }
        )

    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path, new_filename = data_controller.generate_unique_file_path(
        orignal_filename=file.filename, 
        project_id=project_id
    )

    try:

        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)

    except Exception as e:

        logger.error(f'Error while uploading file: {e}')
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {
                'signal': ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )


    # store asset info in Mongodb collection
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client,
    )
    asset_resource = Asset(
        asset_project_id=project.get_id(),
        asset_type=AssetTypeEnums.FILE.value,
        asset_name=new_filename,
        asset_size=os.path.getsize(file_path)
    )

    asset_record = await asset_model.create_asset(asset=asset_resource)


    return JSONResponse(
        status_code = status.HTTP_200_OK,
        content = {
            'signal': ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            'file_id': new_filename,
            'project_id': str(project.get_id()),
            'asset_record': str(asset_record.get_id()),
        }
    )


@data_router.post('/process/{project_id}')
async def process_data(request: Request, project_id: int, process_request: ProcessRequest):

    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    vectordb_controller = VectorDBController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )


    asset_model = await AssetModel.create_instance(
            db_client=request.app.db_client
        )
    
    project_files_ids = {}
    if process_request.file_id:
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.get_id(),
            asset_name=process_request.file_id
        )

        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.FILE_ID_ERROR.value,
                }
            )

        project_files_ids = {
            asset_record.get_id(): asset_record.asset_name
        }
    
    else:
        
        project_files = await asset_model.get_all_project_assets(
            asset_project_id=project.get_id(),
            asset_type=AssetTypeEnums.FILE.value,
        )

        project_files_ids = {
            record.get_id(): record.asset_name
            for record in project_files
        }

    if len(project_files_ids) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.NO_FILES_ERROR.value,
            }
        )

    process_controller = ProcessController(project_id=project_id)

    no_records = 0
    no_files = 0

    chunk_model = await ChunkModel.create_instance(
                        db_client=request.app.db_client
                    )

    if do_reset == 1:

        collection_name = vectordb_controller.create_collection_name(project_id=project.get_id())
        # delete associated collection
        _ = await request.app.vectordb_client.delete_collection(collection_name=collection_name)

        # delete associated vectors collection
        _ = await chunk_model.delete_project_chunks(
            project_id=project.get_id()
        )

    for asset_id, file_id in project_files_ids.items():

        file_content = process_controller.get_file_content(file_id=file_id)

        if file_content is None:
            logger.error(f"Error while processing file: {file_id}")
            continue

        file_chunks = process_controller.process_file_content(
            file_content=file_content,
            file_id=file_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size
        )
        if file_chunks is None or len(file_chunks)==0:
            return JSONResponse(
                status_code = status.HTTP_400_BAD_REQUEST,
                content = {
                    'signal': ResponseSignal.FILE_PROCESS_FAILED.value
                }
            )

        file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=indx+1,
                chunk_project_id=project.get_id(),
                chunk_asset_id=asset_id
            )
            for indx, chunk in enumerate(file_chunks)
        ]

        chunk_model = await ChunkModel.create_instance(
            db_client=request.app.db_client
        )

        no_records +=  await chunk_model.insert_many_chunks(
            chunks=file_chunks_records
        )

        no_files += 1

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'signal': ResponseSignal.FILE_PROCESS_SUCCESS.value,
            "inserted_chunks": no_records,
            "processed_files": no_files

        }
    )

@data_router.delete("/delete-asset/{project_id}")
async def delete_project(request: Request, project_id: int, delete_request: DeleteRequest):
    file_id = delete_request.file_id

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project(project_id=project_id)

    if project is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResponseSignal.PROJECT_NOT_FOUND.value,
            }
        )
    
    chunk_model = await ChunkModel.create_instance(
            db_client=request.app.db_client
        )


    asset_model = await AssetModel.create_instance(
            db_client=request.app.db_client
        )
    

    if file_id is None or len(file_id) == 0:

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResponseSignal.ASSET_NAME_ERROR.value,
            }
        )
    
    asset = await asset_model.get_asset_record(asset_project_id=project.get_id(), asset_name=file_id)
    if asset is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResponseSignal.ASSET_NOT_FOUND.value,
            }
        )


    no_deleted_chunks = await chunk_model.delete_project_chunks(
        project_id=project.get_id(),
        asset_id=asset.get_id(),
    )

    no_deleted_assets = await asset_model.delete_project_assets(
        project_id=project.get_id(),
        asset_name=file_id,
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'signal': ResponseSignal.ASSET_DELETED_SUCCESS.value,
            'no_deleted_chunks': no_deleted_chunks,
            'no_deleted_assets': no_deleted_assets,
            'no_deleted_project': 0
        }
    )

@data_router.delete("/delete-project/{project_id}")
async def delete_project(request: Request, project_id: int):

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project(project_id=project_id)

    if project is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResponseSignal.PROJECT_NOT_FOUND.value,
            }
        )
    
    chunk_model = await ChunkModel.create_instance(
            db_client=request.app.db_client
        )
    
    asset_model = await AssetModel.create_instance(
            db_client=request.app.db_client
        )
    

    no_deleted_chunks = await chunk_model.delete_project_chunks(
        project_id=project.get_id(),
    )

    no_deleted_assets = await asset_model.delete_project_assets(
        project_id=project.get_id(),
    )

    no_deleted_project = await project_model.delete_project(
        project_id=project.get_id(),
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'signal': ResponseSignal.Project_DELETED_SUCCESS.value,
            'no_deleted_chunks': no_deleted_chunks,
            'no_deleted_assets': no_deleted_assets,
            'no_deleted_project': no_deleted_project
        }
    )
