from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson import ObjectId
from datetime import datetime,UTC

class Asset(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    asset_project_id:str
    asset_type:str=Field(...,min_length=1)
    asset_name:str=Field(...,min_length=1)
    asset_size:int=Field(ge=0,default=None)
    asset_config: Optional[dict] = Field(default=None)
    asset_pushed_at:datetime=Field(default=datetime.now(UTC))


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
                    ("asset_project_id",1)
                ],
                "name":"asset_project_id_index_1",
                "unique":False

            },
            {
                "key":[
                    ("asset_project_id",1),
                    ("asset_name",1)
                ],
                "name":"asset_project_id_name_index_1",
                "unique":True

            }

        ]     
