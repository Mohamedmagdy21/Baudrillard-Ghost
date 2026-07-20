from ..QueryRewriterAgentInterface import QueryRewriterAgentInterface
from src.stores.llm.LLMEnums import DocumentTypeEnum
from src.models.db_schema.project import project
from src.models.db_schema.data_chunk import RetrievedDocument
from loguru import logger
from src.models.db_schema.AgenticResponseModel import AgenticResponseModel

from openai import OpenAI

class OpenAiAgent(QueryRewriterAgentInterface):

    def __init__(self, api_key: str,generation_client,embedding_client,vectordb_client ,retry_threshold:float,base_url: str = None , temperature: float = 1,max_retries:int=1):
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=320.0) if base_url else OpenAI(api_key=api_key)
        self.generation_client = generation_client
        self.temperature = temperature
        self.embedding_client=embedding_client
        self.vectordb_client=vectordb_client
        self.retry_threshold=retry_threshold
        self.max_retries=max_retries

    def rewrite(self, query: str, previous_query: str = None) -> str:
        if previous_query:
            prompt = (
                f"The previous rewrite '{previous_query}' returned poor results. "
                f"You must produce a DIFFERENT rewrite than '{previous_query}'. "
                f"Try different phrasing, synonyms, or a more expanded form: {query}"
            )
        else:
            prompt = (
                f"Rewrite the following query as a clear, well-formed question or statement "
                f"suitable for semantic vector search. Fix typos, expand abbreviations, "
                f"remove filler words, and rephrase for clarity. "
                f"The rewritten query MUST differ from the original if the original contains "
                f"typos, grammar issues, or is not a complete phrase.\n\n"
                f"Query: {query}\n\n"
                f"Rewritten query (do not just repeat the original):"
            )

        logger.info(f"[REWRITE] Input: {query}")
        response = self.client.chat.completions.create(
            model=self.generation_client,
            messages=[
            {
                "role": "system",
                "content": (
                "You rewrite search queries for semantic vector search. "
                "Fix typos and grammar, expand abbreviations, use full terms, remove pronouns and filler words. "
                "Always return a clear, well-formed rewrite — even if the only issue is a typo or awkward phrasing. "
                "Return ONLY the rewritten query, nothing else."
            )
            },
            {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=1000,
        )
        result=response.choices[0].message.content.strip()
        if not result:
            result = query  # fallback to original
        logger.info(f"[REWRITE] Output: '{result}'")
        

        return result




   # def evaluate(self, original_query: str, retrieved_chunks: list[dict], rewritten_query: str = None) -> bool:
    #    if not retrieved_chunks:
     #       return False

      
      #  chunks_text = "\n\n".join([c.text or "" for c in retrieved_chunks])

       # prompt = (
        #    f"Query: {original_query}\n\n"
         #   f"Retrieved documents:\n{chunks_text}\n\n"
          #  f"Do these documents contain information to answer the query? "
         #   f"Answer ONLY with YES or NO."
        #)

        #response = self.client.chat.completions.create(
        #    model=self.generation_client,
        #    messages=[{"role": "user", "content": prompt}],
        #    temperature=0,
        #    max_tokens=10,
        #)
        #content = response.choices[0].message.content.strip().upper()
        #decision = "YES" in content and "NO" not in content.split("YES")[0]

        #return decision    

    
    def evaluate(self, retrieved_chunks: list,  threshold: float ) -> bool:
        if not retrieved_chunks:
            return False

        avg_score = sum(c.score for c in retrieved_chunks) / len(retrieved_chunks)
        texts = [doc.text for doc in retrieved_chunks]

        logger.info(f"[EVALUATE] Avg score: {avg_score:.4f} (threshold={threshold})")

        return avg_score >= threshold,avg_score,texts

    def run(self, query: str, project:project,collection_name:str ,limit: int = 5):

        history = []
        for attempt in range(self.max_retries):
            
            
            if attempt == 0:
                rewritten = self.rewrite(query)
            else:
                rewritten = self.rewrite(query, previous_query=history[-1]["rewritten"],
                                        )

            # embed & search
            logger.info(f"[AGENT] Rewritten query: '{rewritten}'")
            vector = self.embedding_client.embed_text(rewritten, document_type=DocumentTypeEnum.Query.value)
            docs = self.vectordb_client.search_by_vector(collection_name, vector, limit=limit)

            # score should return
            passed,avg_score,retrieved = self.evaluate(retrieved_chunks= docs,threshold=self.retry_threshold)
            logger.info(f"[AGENT] Attempt {attempt + 1}/{self.max_retries} - docs_found={bool(docs)} eval_passed={passed}")

            if passed:
                history.append({"rewritten": rewritten, "avg_score":avg_score,"attempt":attempt+1,"retrieved_docs":retrieved})
                best = max(history, key=lambda x: x["avg_score"])
                return AgenticResponseModel(**best)



                


            history.append({"rewritten": rewritten, "feedback": "returned irrelevant content", "avg_score":avg_score,"attempt":attempt+1,"retrieved_docs":retrieved})


        best = max(history, key=lambda x: x["avg_score"])  

        return AgenticResponseModel(**best)  



        #return docs, query, max_retries      