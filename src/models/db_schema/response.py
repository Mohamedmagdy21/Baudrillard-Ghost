from pydantic import BaseModel, Field, field_validator

class Response(BaseModel):
    id: str
    created_at: float
    output_text: str

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if not value:
            raise ValueError("id cannot be empty")
        return value

    @field_validator("output_text")
    @classmethod
    def validate_output_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("output_text cannot be empty")
        return value

    @classmethod
    def get_indexes(cls):

        return[
            {
                "key":[
                    ("response_project_id",1)
                ],
                "name":"response_project_id_index_1",
                "unique":True

            }
        ]         