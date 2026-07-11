from qdrant_client import models, QdrantClient
from ..VectorDBinterface import VectorDBinterface
from ..VectorDBEnums import VectorDBEnums,DistanceMethodEnums
from src.models.db_schema.data_chunk import RetrievedDocument
import logging
from typing import List
import uuid



class QdrantDB(VectorDBinterface):

    def __init__(self,db_path:str,distance_method:str):

        self.client=None
        self.db_path=db_path
        self.distance_method=distance_method

        if self.distance_method==DistanceMethodEnums.COSINE.value:
            self.distance_method=models.Distance.COSINE

        elif self.distance_method==DistanceMethodEnums.DOT.value:
            self.distance_method=models.Distance.DOT

        self.logger=logging.getLogger(__name__)   

    def connect(self):
        self.client=QdrantClient(path=self.db_path) 


    def disconnect(self):
        self.client=None        


    def does_collection_exist(self, collection_name: str) -> bool:
        return   self.client.collection_exists(collection_name=collection_name)


    def get_collection_info(self, collection_name: str):
        return  self.client.get_collection(collection_name=collection_name)

    
    def list_all_collections(self) -> List:
        return self.client.get_collections()

    def delete_collection(self, collection_name: str):
        if self.does_collection_exist(collection_name=collection_name):
            self.client.delete_collection(collection_name=collection_name)

            
    def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict = {}, record_id: str = None):

        if not self.does_collection_exist(collection_name=collection_name):
            self.logger.error("can not insert new record into a non-existing container")
            return False

        payload = {
               "text": text,
                 **metadata
        }  

        self.client.upload_points(
            collection_name=collection_name,
            points=[models.PointStruct(id=record_id
            ,payload=payload,
            vector=vector
            )
            ]
            )

        return True   


    def insert_many(self, collection_name: str, texts: list[str], vectors: list[list[float]],batch_size:int=1, metadatas: list[dict] = None, record_ids: list = None):
        
        if len(texts) != len(vectors):

            raise ValueError(
            "texts and vectors must have the same length."
        )
        if metadatas is not None and len(metadatas) != len(texts):
            raise ValueError(
            "metadatas must have the same length as texts."
        )

        if record_ids is not None and len(record_ids) != len(texts):
           raise ValueError(
           "record_ids must have the same length as texts."
        )

        
        if metadatas is None:
            metadatas=[None] * len(texts)

        if record_ids is None:
            record_ids = [str(uuid.uuid4()) for _ in range(len(texts))]

        for i in range(0,len(texts),batch_size):
            batch_text=texts[i:i+batch_size]
            batch_metadata=metadatas[i:i+batch_size]
            batch_vectors=vectors[i:i+batch_size] 
            batch_record_ids=record_ids[i:i+batch_size]

            


            points=[ models.PointStruct(
                id=batch_record_ids[x],
                payload={
                    "text":batch_text[x],
                    **(batch_metadata[x] or {})
                },
                vector=batch_vectors[x]
            )
            for x in range(len(batch_text))


            ]

            self.client.upload_points(
            collection_name=collection_name,
            points=points
            )
        return True    
   

            


    def create_collection(self, collection_name: str, collection_size: int, do_reset: bool = False):

        if do_reset:
            _ = self.client.delete_collection(collection_name=collection_name)
        
        if not self.client.collection_exists(collection_name=collection_name):

            _= self.client.create_collection(
                     collection_name=collection_name,
                     vectors_config=models.VectorParams(size=collection_size, distance=self.distance_method),
                    )  
            return True

        return False  

    def search_by_vector(self, collection_name: str, vector: list[float], limit: int=5): 
        results=self.client.query_points(
        collection_name=collection_name,
        query=vector,
        limit=limit,
        )   

        if not results or not results.points:
            return None

        return [

            RetrievedDocument(**{
                "score":result.score,
                "text": result.payload["text"]
            })

            for result in results.points
        ]    



 



