from ..RerankerInterface import RerankerInterface
from ..RerankerEnums import RerankerEnums
from src.models.db_schema.data_chunk import RetrievedDocument
import cohere
import logging


class CohereReranker(RerankerInterface):

    def __init__(self, api_key: str, model: str = None):
        self.client = cohere.ClientV2(api_key=api_key)
        self.model = model
        self.enums = RerankerEnums
        self.logger = logging.getLogger(__name__)

    def set_rerank_model(self, model: str) -> None:
        self.model = model

    def rerank(self, query: str, documents: list[str], top_n: int = None) -> list[RetrievedDocument]:
        if not self.client:
            self.logger.error("Cohere client not initialized")
            return None

        if not self.model:
            self.logger.error("Rerank model not defined")
            return None

        if not documents:
            return []

        if top_n is None:
            top_n = len(documents)

        response = self.client.rerank(
            model=self.model,
            query=query,
            documents=documents,
            top_n=top_n,
        )

        if not response or not response.results:
            self.logger.error("Cohere rerank failed")
            return None

        reranked = []
        for result in response.results:
            idx = result.index
            reranked.append(RetrievedDocument(
                text=documents[idx],
                score=None,
                rerank_score=result.relevance_score,
            ))

        return reranked
