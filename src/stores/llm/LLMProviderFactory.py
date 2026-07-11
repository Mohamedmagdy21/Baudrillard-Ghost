from .LLMEnums import LLMEnums
from .providers.CohereProvider import CohereProvider
from .providers.GlmProvider import GlmProvider

class LLMProvideFactory:

    def __init__(self,config:dict):
        self.config=config

    def create(self,provider:str):    
        if provider == LLMEnums.GLM.value:
            return GlmProvider(
                api_key=self.config.ZAI_API_KEY,
                api_url=self.config.ZAI_URL,
                default_input_max_tokens=self.config.DEFAULT_INPUT_MAX_CHARACTERS,
                default_output_max_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE


            )
        if provider==LLMEnums.COHERE.value:
            return CohereProvider(api_key=self.config.COHERE_API_KEY,
            default_input_max_tokens=self.config.DEFAULT_INPUT_MAX_CHARACTERS,
            default_output_max_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
            default_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
            )

        return None
