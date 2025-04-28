from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from helpers.config import get_settings, Settings
from fastapi.responses import JSONResponse

from controllers.VectorDBController import VectorDBController
from models import ResponseSignal
from routes.schemes.vectordb import PushRequest, SearchRequest
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
        template_parser=request.app.template_parser,
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
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
                "inserted_items_count": inserted_items_count
            }
        )

@vectordb_router.post('/index/info/{project_id}')
async def get_project_index_info(request: Request, project_id: str):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)

    vectordb_controller = VectorDBController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    collection_info = vectordb_controller.get_vector_db_collection_info(project=project)

    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.VECTORDB_COLLECTION_RETRIVED.value,
                "collection": collection_info
            }
        )


@vectordb_router.post('/index/search/{project_id}')
async def search_index(request: Request, project_id: str, search_request: SearchRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)

    vectordb_controller = VectorDBController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    result = vectordb_controller.search_vector_db_collection(
        project=project,
        text=search_request.text, 
        limit=search_request.limit
    )

    if not result:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.VECTORDB_SEARCH_ERROR.value
                }
            )
    
    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.VECTORDB_SEARCH_SUCCESS.value,
                "result": [record.dict() for record in result]
            }
        )


@vectordb_router.post('/index/answer/{project_id}')
async def answer_index(request: Request, project_id: str, search_request: SearchRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)

    vectordb_controller = VectorDBController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    answer, full_prompt, chat_history = vectordb_controller.answer_rag_question(
        project=project,
        query=search_request.text,
        limit=search_request.limit,
    )

    if not answer:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.RAG_ANSWER_ERROR.value
                }
        )
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history
        }
    )