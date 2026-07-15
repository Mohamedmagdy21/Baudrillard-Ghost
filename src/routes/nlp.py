import collections
from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
import os
from fastapi.responses import JSONResponse
import logging
from .schemes.nlp import PushRequest, SearchRequest
from src.models.ProjectModel import ProjectModel
from src.models.ChunkModel import ChunkModel
from src.controllers.NLPController import NLPController
from src.models.enums.ResponseEnum import ResponseSignal

logger=logging.getLogger('uvicorn.error')

nlp_router=APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1","nlp"]
)

@nlp_router.post("/push/index/{project_id}")
async def push_index(request:Request,project_id:str,PushRequest:PushRequest):

    #project_model=await ProjectModel.create_instance(db_client=request.app.db_client)
    
    #chunk_model=await ChunkModel.create_instance(db_client=request.app.db_client)

    project_model = request.app.project_model
    chunk_model=request.app.chunk_model

    project=await project_model.get_project_or_create_one(
        project_id=project_id
    )

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal":ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            },
        )

    nlp_controller=request.app.nlp_controller   
    #nlp_controller=NLPController(vectordb_client=request.app.vectordb_client,embedding_model=request.app.embedding_client,generation_model=request.app.generation_client)

    has_records=True
    page_num=1
    inserted_items_counts=0
    id=0
    first_page=True
    while has_records :
       
     page_chunks=await chunk_model.get_project_chunk(project_id=project.id,page_num=page_num) 

     if len(page_chunks):
        page_num+=1

     if not page_chunks and len(page_chunks)==0:
        has_records=False 
        break 
     chunk_ids=list(range(id,id+len(page_chunks))) 
     id+=len(page_chunks)


     is_inserted= await nlp_controller.index_into_vector_db(
        project=project,
        chunks=page_chunks,
        do_reset=PushRequest.do_reset if first_page else False,
        chunk_ids=chunk_ids
     )

     first_page=False

     if not is_inserted:
        return JSONResponse(
            
            content={
                      "signal":ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
                      "inserted_items_count": inserted_items_counts
            },
        )
        
     inserted_items_counts+=len(page_chunks)   
     

    return is_inserted    

@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request:Request,project_id:str):

    project_model = request.app.project_model

    project=await project_model.get_project_or_create_one(
        project_id=project_id
    )
    
    nlp_controller=request.app.nlp_controller 
    #nlp_controller=NLPController(vectordb_client=request.app.vectordb_client,embedding_model=request.app.embedding_client,generation_model=request.app.generation_client)

    collection_info=nlp_controller.get_vector_db_collection_info(project=project)

    return JSONResponse(
            
            content={
                      "signal":ResponseSignal.VECTOR_COLLECTION_RETRIEVED.value,
                      "collection_info": collection_info.model_dump()
            },
        )


@nlp_router.post("/index/search/{project_id}")
async def search_index(request:Request,project_id:str,search_request:SearchRequest):

    project_model = request.app.project_model

    project=await project_model.get_project_or_create_one(
        project_id=project_id
    )
    
    nlp_controller=request.app.nlp_controller 
    #nlp_controller=NLPController(vectordb_client=request.app.vectordb_client,embedding_model=request.app.embedding_client,generation_model=request.app.generation_client)

    results=nlp_controller.search_vector_db_collection(project=project,text=search_request.text,limit=search_request.limit)

    if not results:
        return JSONResponse(

            status_code=status.HTTP_400_BAD_REQUEST,
            
            content={
                      "signal":ResponseSignal.VECTOR_DB_SEARCH_ERROR.value,
            },
        )

    return JSONResponse(
            
            content={
                      "signal":ResponseSignal.VECTOR_DB_SEARCH_SUCCESS.value,
                      "retrieved list": [r.model_dump() for r in results]
            },
        )    



@nlp_router.post("/index/answer/{project_id}")
async def rag_answer(request:Request,project_id:str,search_request:SearchRequest):

    project_model = request.app.project_model

    project=await project_model.get_project_or_create_one(
        project_id=project_id
    )
    
    nlp_controller=request.app.nlp_controller 

    response, full_prompt=nlp_controller.answer_rag_question(project=project,query=search_request.text,limit=search_request.limit)

    if not response:
        return JSONResponse(
            status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.ANSWER_GENERATION_FAILED.value
            }
        )

    return JSONResponse(
        content={
            "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "answer": response,
            "full_prompt":full_prompt
        }
    )