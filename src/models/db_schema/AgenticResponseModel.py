from typing import Optional
from pydantic import BaseModel, field_validator


class AgenticResponseModel(BaseModel):
    rewritten: str
    feedback: Optional[str] = None
    avg_score: float
    attempt: int
    retrieved_docs: list[str]

    @field_validator("rewritten")
    @classmethod
    def validate_rewritten(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("rewritten cannot be empty.")
        return value

    @field_validator("feedback")
    @classmethod
    def validate_feedback(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not value.strip():
            raise ValueError("feedback cannot be an empty string.")
        return value

    @field_validator("avg_score")
    @classmethod
    def validate_avg_score(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("avg_score must be between 0 and 1.")
        return value

    @field_validator("attempt")
    @classmethod
    def validate_attempt(cls, value: int) -> int:
        if value < 1:
            raise ValueError("attempt must be at least 1.")
        return value

    @field_validator("retrieved_docs")
    @classmethod
    def validate_retrieved_docs(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("retrieved_docs cannot be empty.")

        for doc in value:
            if not doc.strip():
                raise ValueError("retrieved_docs cannot contain empty strings.")

        return value