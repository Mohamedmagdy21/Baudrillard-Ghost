from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson import ObjectId
from .chunk_metadata import ChunkMetaData


class DataChunk(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    id: Optional[str] = Field(default=None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: ChunkMetaData
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: str
    chunk_asset_id:str

    @field_validator('id', mode='before')
    @classmethod
    def convert_object_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    @classmethod
    def get_indexes(cls):

        return[
            {
                "key":[
                    ("chunk_project_id",1)
                ],
                "name":"chunk_project_id_index_1",
                "unique":False

            }
        ] 

    @field_validator("chunk_metadata", mode="before")
    @classmethod
    def parse_metadata(cls, v):
        if isinstance(v, dict):
            return ChunkMetaData(**v)
        return v        


class RetrievedDocument(BaseModel):
    text:str
    score:Optional[float]=None
    rerank_score:Optional[float]=None
