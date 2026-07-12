from ..LLMinterface import LLMInterface
from openai import OpenAI
import logging
from ..LLMEnums import OpenAiEnums


class GlmProvider(LLMInterface):
    def __init__(self, api_key: str, api_url: str=None,default_input_max_tokens: int=1024,default_output_max_tokens: int=1024,default_temperature: float=0.7):
        self.client = OpenAI(api_key=api_key,base_url=api_url)
        self.api_url = api_url
        self.default_input_max_tokens = default_input_max_tokens
        self.default_output_max_tokens = default_output_max_tokens
        self.default_temperature = default_temperature

        self.generation_model = None
        self.embedding_model = None
        self.embedding_dimensions = None

        self.enums=OpenAiEnums

        

        self.logger = logging.getLogger(__name__)

   

    def set_generation_model(self, model: str):
        self.generation_model= model

    def set_embedding_model(self, model: str,embedding_dimensions: int):
        self.embedding_model = model
        self.embedding_dimensions = embedding_dimensions

    def process_text(self, text: str) -> str:
        return text[:self.default_input_max_tokens].strip()

    def generate_text(self, system_prompt: str, user_prompt: str, max_output_tokens: int,temperature:float=None) -> str:
        if not self.client:
            self.logger.error("Client not initialized")
            return None

        if not self.generation_model:
            self.logger.error("Generation model not initialized")
            return None

        if not max_output_tokens:
            max_output_tokens = self.default_output_max_tokens

        if not temperature:
            temperature = self.default_temperature

        prompt = self.construct_prompt(system_prompt, user_prompt)    

        response = self.client.responses.create(
            model=self.generation_model,
            input=prompt,
            store=True,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        )

        if not response.output_text or len(response.output_text) == 0:
            self.logger.error("Failed to generate text")
            return None

        return response.output_text

    def embed_text(self, text: str,document_type:str=None) -> str:

        if not self.client:
            self.logger.error("Client not initialized")
            return None

        if not self.embedding_model:
            self.logger.error("Embedding model not initialized")
            return None

        if not self.embedding_dimensions:
            self.logger.error("Embedding dimensions not initialized")

        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text,
            dimensions=self.embedding_dimensions
        )

        if not response.data or not response or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Failed to embed text")
            return None

        return response.data[0].embedding

    def construct_prompt(self, system_prompt: str, user_prompt: str, role:str=None) -> str:
        final_prompt=[
            {
            "role": OpenAiEnums.System.value,
            "content": system_prompt
            },
            {
            "role": OpenAiEnums.User.value,
            "content": self.process_text(user_prompt)
            }
            ]
            
        return final_prompt

    