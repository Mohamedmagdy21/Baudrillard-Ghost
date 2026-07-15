from abc import ABC, abstractmethod
from typing import Optional

class QueryRewriterAgentInterface(ABC):

    @abstractmethod
    def rewrite(self, query: str, previous_query: Optional[str] = None, previous_results_summary: Optional[str] = None) -> str:
        """Transform the query for better vector search retrieval"""
        pass

    @abstractmethod
    def evaluate(self, query: str, retrieved_chunks: list) -> bool:
        """Return True if chunks are relevant enough, False to retry"""
        pass

    @abstractmethod
    def run(self, query: str, max_retries: int = 3) -> tuple:
        """Agentic loop: returns (retrieved_docs, final_rewritten_query) or (None, None)"""
        pass