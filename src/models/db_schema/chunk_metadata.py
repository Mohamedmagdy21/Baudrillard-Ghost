from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class ChunkMetaData(BaseModel):

    book_name: str = Field(..., min_length=1)
    chapter: str = Field(..., min_length=1)
    page: int = Field(..., ge=0)
    page_range: str

    @field_validator("page_range")
    @classmethod
    def validate_page_range(cls, v: str) -> str:
        if not re.match(r"^\d+(-\d+)?$", v):
            raise ValueError("page_range must be like '12' or '12-15'")
        return v

    @field_validator("book_name", "chapter")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()