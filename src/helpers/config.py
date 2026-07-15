from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str

    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    MONGO_URL: str
    MONGODB_DATABASE: str

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND:str
    ZAI_API_KEY:str
    COHERE_API_KEY:str

    ZAI_URL:str

    GENERATION_MODEL:str=None
    EMBEDDING_MODEL:str=None
    EMBEDDING_MODEL_DIMENSIONS:int=None
    DEFAULT_INPUT_MAX_TOKENS:int=None
    GENERATION_DEFAULT_MAX_TOKENS:int=None
    GENERATION_DEFAULT_TEMPERATURE:float=None

    VECTOR_DB_BACKEND:str
    VECTOR_DB_PATH:str
    VECTOR_DB_DISTANCE:str=None

    
    DEFAULT_LANGAUGE:str="en"

    REWRITER_API_KEY:str
    REWRITER_BASE_URL:str
    REWRITER_MODEL:str

    RETRY_THRESHOLD:float
    MAX_RETRIES:int






    class Config:
        env_file= "src/.env"


def get_settings():
    return Settings()