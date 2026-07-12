from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from src.routes import base
from src.routes import data,nlp
import asyncio
from pymongo import AsyncMongoClient # Native async client
from src.helpers.config import get_settings
from src.stores.llm.LLMProviderFactory import LLMProvideFactory
from src.stores.vectordb.VectorDBFactory import VectorDBFactory
from src.models.AssetModel import AssetModel
from src.models.ProjectModel import ProjectModel
from src.models.ChunkModel import ChunkModel
from src.models.ResponseModel import ResponseModel
from src.stores.llm.templates.template_parser import TemplateParser
from src.controllers.NLPController import NLPController



@asynccontextmanager
async def lifespan(app: FastAPI):

    settings=get_settings()

    app.mongo_conn=AsyncMongoClient(settings.MONGO_URL)
    await app.mongo_conn.aconnect()
    app.db_client=app.mongo_conn[settings.MONGODB_DATABASE]

    app.project_model = await ProjectModel.create_instance(db_client=app.db_client)
    app.asset_model = await AssetModel.create_instance(db_client=app.db_client)
    app.chunk_model = await ChunkModel.create_instance(db_client=app.db_client)

    # newly added for the LLM conversation history
    app.response_model = await ResponseModel.create_instance(db_client=app.db_client)

    # This guarantees your app fails immediately if your local Docker/Atlas Mongo instance is offline
   
    llm_provider_factory=LLMProvideFactory(settings)
    
    #embedding_client
    app.embedding_client=llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    
    if app.embedding_client:
        app.embedding_client.set_embedding_model(model=settings.EMBEDDING_MODEL,embedding_dimensions=settings.EMBEDDING_MODEL_DIMENSIONS)

    # generation client
    app.generation_client=llm_provider_factory.create(provider=settings.GENERATION_BACKEND)

    if app.generation_client:
        app.generation_client.set_generation_model(model=settings.GENERATION_MODEL)

    vectordb_factory = VectorDBFactory(settings)
    app.vectordb_client=vectordb_factory.create(provider=settings.VECTOR_DB_BACKEND)
    
    if app.vectordb_client:
        app.vectordb_client.connect()

    app.template_parser=TemplateParser(
        language=settings.DEFAULT_LANGAUGE,
        default_langauge=settings.DEFAULT_LANGAUGE,
        
    )    

    app.nlp_controller=NLPController(vectordb_client=app.vectordb_client,embedding_model=app.embedding_client,generation_model=app.generation_client,template_parser=app.template_parser)




    yield

    # 2. Teardown Phase (App Shutdown)
    # Await the connection close to cleanly flush background I/O operations
    await app.mongo_conn.aclose()
    _= app.vectordb_client.disconnect()


app=FastAPI(lifespan=lifespan)



app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
