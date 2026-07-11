from abc import ABC, abstractmethod
from typing import List
from src.models.db_schema.data_chunk import RetrievedDocument

class VectorDBinterface(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def does_collection_exist(self,collection_name:str) ->bool:
        pass

    @abstractmethod
    def list_all_collections(self) -> List:
        pass


    @abstractmethod
    def get_collection_info(self,collection_name:str):
        pass


    @abstractmethod
    def delete_collection(self,collection_name:str):
        pass

    @abstractmethod
    def create_collection(self,collection_name:str,collection_size:int,do_reset:bool=False):
        pass

    @abstractmethod
    def insert_one(self,collection_name:str,text:str,vector:list,metadata:dict={},record_id:str=None):
        pass

    @abstractmethod
    def insert_many(self,collection_name:str,texts:list,vectors:list,batch_size:int,metadatas:list=None,record_ids:list=None):
        pass

    @abstractmethod
    def search_by_vector(self,collection_name:str,vector:list,limit:int) -> list[RetrievedDocument]:
        pass