from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson import ObjectId


class Response(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    id: Optional[str] = Field(default=None, alias="_id")
    session_id: str
    response_project_id: str
    user_query: str
    output_text: str
    created_at: float

    @field_validator("id", mode="before")
    @classmethod
    def convert_object_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("session_id cannot be empty")
        return value

    @field_validator("user_query")
    @classmethod
    def validate_user_query(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("user_query cannot be empty")
        return value

    @field_validator("output_text")
    @classmethod
    def validate_output_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("output_text cannot be empty")
        return value

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("response_project_id", 1), ("session_id", 1)],
                "name": "project_session_index",
                "unique": False
            },
            {
                "key": [("session_id", 1), ("created_at", 1)],
                "name": "session_created_at_index",
                "unique": False
            }
        ]
