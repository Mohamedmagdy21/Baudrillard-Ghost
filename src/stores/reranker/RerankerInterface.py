from abc import ABC, abstractmethod
from src.models.db_schema.data_chunk import RetrievedDocument


class RerankerInterface(ABC):

    @abstractmethod
    def set_rerank_model(self, model: str) -> None:
        pass

    @abstractmethod
    def rerank(self, query: str, documents: list[str], top_n: int = None) -> list[RetrievedDocument]:
        pass
