from src.helpers.config import Settings,get_settings
from .providers import QdrantDB
from .VectorDBEnums import VectorDBEnums
from src.controllers.BaseController import BaseController


class VectorDBFactory():

    def __init__(self,config:dict):
        self.config=config
        self.base_controller=BaseController()
        self.db_path=self.base_controller.get_database_path(db_name=self.config.VECTOR_DB_PATH)


    def create(self,provider:str):
        if provider==VectorDBEnums.QDRANT.value:
            return QdrantDB( db_path=self.db_path,
            distance_method=self.config.VECTOR_DB_DISTANCE
            )  

        return None     