
from src.models.db_schema.data_chunk import DataChunk
from .BaseDataModel import BaseDataModel
from .db_schema import project
from .enums.DataBaseEnum import DataBaseEnum
from pymongo import InsertOne


class ChunkModel(BaseDataModel):

    def __init__(self,db_client:object):
        super().__init__(db_client=db_client)
        self.collection=self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    @classmethod
    async def create_instance(cls,db_client:object):
        instance=cls(db_client)  
        await instance.init_collection()
        return instance     

    async def init_collection(self):
        all_collection = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collection:
            self.collection=self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
            indexes=DataChunk.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )    

    async def create_chunk(self,chunk:DataChunk):
        result=await self.collection.insert_one(chunk.model_dump())
        chunk.id=result.inserted_id
        return chunk

    async def get_chunk(self,chunk_id:str):
        result = await self.collection.find_one({"id":chunk_id})  

        if result is None:
            return None

        return DataChunk(**result)    

    async def insert_chunks(self,chunks:list,batch_size:int=50):
        
        for i in range(0,len(chunks),batch_size):
            batch=chunks[i:i+batch_size]
            operations=[

                InsertOne(chunk.model_dump())

                for chunk in batch
            ]

            await self.collection.bulk_write(operations)

        return len(chunks)

    async def delete_chunks_by_project_id(self,project_id):
        result=await self.collection.delete_many({
            "chunk_project_id":project_id
        })
        return result.deleted_count

    async def get_project_chunk(self,project_id:str,page_num:int=1,page_size:int=50):
        results= await self.collection.find({
            "chunk_project_id":project_id
            }).skip((page_num-1)*page_size).limit(page_size).to_list(length=None)

        return [
            DataChunk(**record)
            for record in results
        ]    


            


