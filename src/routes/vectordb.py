from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from helpers.config import get_settings, Settings
from fastapi.responses import JSONResponse

from controllers.VectorDBController import VectorDBController
from models import ResponseSignal
from routes.schemes.vectordb import PushRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schemes import DataChunk

import logging

logger = logging.getLogger('uvicorn.error')

vectordb_router = APIRouter(
    prefix='/api/v1/vectordb',
    tags=['api_v1_vectordb']
)


@vectordb_router.post('/index/push/{project_id}')
async def index_project(request: Request, project_id: str, push_request: PushRequest):
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    chunk_model = await ChunkModel.create_instance(
                        db_client=request.app.db_client
                    )

    project = await project_model.get_project_or_create_one(project_id=project_id)


    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND.value,
            }
        )

    vectordb_controller = VectorDBController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
    )

    has_record = True 
    page_no = 1
    inserted_items_count = 0
    indx = 0

    while has_record:
        page_chunks = await chunk_model.get_project_chunks(project_id=project.get_id(), page_no=page_no)
        if len(page_chunks):
            page_no += 1

        if not page_chunks or len(page_chunks) == 0:
            has_record = False
            break

        chunks_ids =  list(range(indx, indx + len(page_chunks)))
        indx += len(page_chunks)
        
        is_inserted = vectordb_controller.index_into_vectordb(
            project=project,
            chunks=page_chunks,
            do_reset=push_request.do_reset,
            chunks_ids=chunks_ids
        )

        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value
                }
            )
        
        inserted_items_count += len(page_chunks)
        
        return JSONResponse(
            content={
                "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
                "inserted_items_count": inserted_items_count
            }
        )
