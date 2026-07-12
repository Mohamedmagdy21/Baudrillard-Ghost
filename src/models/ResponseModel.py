from src.models.db_schema.response import Response
from .BaseDataModel import BaseDataModel
from .db_schema import project
from .enums.DataBaseEnum import DataBaseEnum
from pymongo import InsertOne

class ResponseModel(BaseDataModel):

    def __init__(self,db_client:object):

        super().__init__(db_client=db_client)
        self.collection=self.collection=self.db_client[DataBaseEnum.COLLECTION_RESPONSES_HISTORY.value]


    @classmethod
    async def create_instance(cls,db_client:object):
        instance=cls(db_client)  
        await instance.init_collection()
        return instance 


    async def init_collection(self):
        all_collection = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_RESPONSES_HISTORY.value not in all_collection:
            self.collection=self.db_client[DataBaseEnum.COLLECTION_RESPONSES_HISTORY.value]
            indexes=Response.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )    

    async def create_chunk(self,response:Response):
        result=await self.collection.insert_one(response.model_dump())
        response.id=result.inserted_id
        return response

    async def get_response(self,response_id:str):
        result = await self.collection.find_one({"id":response_id})  

        if result is None:
            return None

        return Response(**result)     

    async def insert_response(self,response:Response):
        
       await self.collection.insert_one(response.model_dump())

    async def delete_responses_by_project_id(self,project_id):
        result=await self.collection.delete_many({
            "response_project_id":project_id
        })
        return result.deleted_count  

    async  def get_response_by_project_id(self,project_id):
        results= await self.collection.find(
            {
                 "response_project_id":project_id

        }
        )
        return Response(**results)
