from abc import ABC, abstractmethod

class LLMInterface(ABC):

    @abstractmethod
    def set_generation_model(self, model: str) -> str:
        pass

    @abstractmethod
    def set_embedding_model(self, model: str,embedding_dimensions: int) -> str:
        pass



    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        pass

    @abstractmethod
    def embed_text(self, text: str,document_type:str=None) -> str:
        pass

    @abstractmethod
    def generate_text(self, prompt: str, max_output_tokens: int,temprature:float=None) -> str:
        pass

    @abstractmethod
    def construct_prompt(self, prompt: str, role:str) -> str:
        pass
   
