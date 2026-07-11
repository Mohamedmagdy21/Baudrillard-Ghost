from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson import ObjectId


class project(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    id: Optional[str] = Field(default=None, alias="_id")
    project_id: str = Field(..., min_length=1)

    @field_validator('id', mode='before')
    @classmethod
    def convert_object_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    @field_validator('project_id')
    @classmethod
    def validate_project_id(cls, v):
        if not v.isalnum():
            raise ValueError('project_id must be alphanumeric')
        return v

    @classmethod
    def get_indexes(cls):

        return[
            {
                "key":[
                    ("project_id",1)
                ],
                "name":"project_id_index_1",
                "unique":True

            }
        ] 