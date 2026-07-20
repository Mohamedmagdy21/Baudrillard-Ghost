from ..RerankerInterface import RerankerInterface
from ..RerankerEnums import RerankerEnums
from src.models.db_schema.data_chunk import RetrievedDocument
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import logging


class SentenceTransformersReranker(RerankerInterface):

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()
        self.enums = RerankerEnums
        self.logger = logging.getLogger(__name__)

    def set_rerank_model(self, model: str) -> None:
        self.model_name = model
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForSequenceClassification.from_pretrained(model)
        self.model.eval()

    def rerank(self, query: str, documents: list[str], top_n: int = None) -> list[RetrievedDocument]:
        if not documents:
            return []

        if top_n is None:
            top_n = len(documents)

        queries = [query] * len(documents)

        with torch.no_grad():
            inputs = self.tokenizer(
                queries,
                documents,
                padding=True,
                truncation=True,
                return_tensors="pt",
                max_length=512,
            )
            scores = self.model(**inputs).logits.squeeze(-1)

        scores_list = scores.tolist()
        if isinstance(scores_list, float):
            scores_list = [scores_list]

        ranked_indices = sorted(
            range(len(scores_list)),
            key=lambda i: scores_list[i],
            reverse=True,
        )[:top_n]

        return [
            RetrievedDocument(
                text=documents[i],
                score=None,
                rerank_score=scores_list[i],
            )
            for i in ranked_indices
        ]
