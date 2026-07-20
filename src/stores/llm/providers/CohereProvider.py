from email import message
from ..LLMinterface import LLMInterface
from ..LLMEnums import CohereEnums,DocumentTypeEnum
import cohere
import os
import logging


class CohereProvider(LLMInterface):
    def __init__(self, api_key: str,default_input_max_tokens: int=1024,default_output_max_tokens: int=1024,default_temperature: float=0.7):
        self.client = cohere.ClientV2(api_key=api_key)
        self.default_input_max_tokens = default_input_max_tokens
        self.default_output_max_tokens = default_output_max_tokens
        self.default_temperature = default_temperature

        self.generation_model = None
        self.embedding_model = None
        self.embedding_dimensions = None

        self.enums=CohereEnums
        

        self.logger = logging.getLogger(__name__)


    def set_generation_model(self,model):
        self.generation_model=model

    def set_embedding_model(self, model: str, embedding_dimensions: int) -> str:
        self.embedding_model=model
        self.embedding_dimensions=embedding_dimensions

    def construct_prompt(self, prompt: str, role: str) -> str:
        messages=[
            {
                "role":CohereEnums.USER.value,
                "content":prompt
            }
        ] 

    def embed_text(self, text: str, document_type: str = None) -> str:

        if not self.client:
            self.logger.error("Client not initialized")
            return None

        if not self.embedding_model:
            self.logger.error("embedding model not defined")
            return None 

        input_type= CohereEnums.DOCUMENT.value
        if document_type== DocumentTypeEnum.Query.value:
            input_type=CohereEnums.QUERY.value


        
        response = self.client.embed(
              texts=[text],
              model=self.embedding_model,
              input_type=input_type,
              embedding_types=["float"],
             ) 

        if not response or not response.embeddings or not response.embeddings.float_:
            self.logger.error("embedding failed")
            return None

        return response.embeddings.float[0] 

    def embed_text_batch(self, texts: list, document_type: str = None) -> list:
        if not self.client or not self.embedding_model:
            return None

        input_type = CohereEnums.DOCUMENT.value
        if document_type == DocumentTypeEnum.Query.value:
            input_type = CohereEnums.QUERY.value

        all_embeddings = []
        batch_size = 96
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.embed(
                texts=batch,
                model=self.embedding_model,
                input_type=input_type,
                embedding_types=["float"],
            )
            all_embeddings.extend(response.embeddings.float)

        return all_embeddings       



    def process_text(self, text: str) -> str:
        return text[:self.default_input_max_tokens].strip()          

    def generate_text(self, system_prompt: str = None, user_prompt: str = None, max_output_tokens: int = None, temperature: float = None, chat_history: list = None) -> str:
        if not self.client:
            self.logger.error("Client not initialized")
            return None

        if not self.generation_model:
            self.logger.error("generational model not defined")
            return None    

        
        if not max_output_tokens:
            max_output_tokens=self.default_output_max_tokens

        if not temperature:
            temperature=self.default_temperature

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if chat_history:
            messages.extend(chat_history)
        messages.append({"role": "user", "content": self.process_text(user_prompt or "")})

        try:
            response=self.client.chat(
                model=self.generation_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_output_tokens
            )
        except Exception as e:
            self.logger.error(f"Generation API error: {e}")
            return None

        if not response or not response.message.content:
            self.logger.error("Failed to generate text")
            return None
        
        return response.message.content[0].text

    
