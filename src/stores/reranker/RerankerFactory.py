from .RerankerEnums import RerankerEnums
from .providers.CohereReranker import CohereReranker
from .providers.SentenceTransformersReranker import SentenceTransformersReranker


class RerankerFactory:

    def __init__(self, config: dict):
        self.config = config

    def create(self, provider: str):
        if provider == RerankerEnums.COHERE.value:
            return CohereReranker(
                api_key=self.config.COHERE_API_KEY,
                model=self.config.RERANKER_MODEL,
            )

        if provider == RerankerEnums.SENTENCE_TRANSFORMERS.value:
            return SentenceTransformersReranker(
                model_name=self.config.RERANKER_MODEL,
            )

        return None
