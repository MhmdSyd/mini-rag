from ..LLMInterface import LLMInterface
from ..LLMEnums import OLLAMAEnums
import ollama
import logging 
from typing import Union, List

class OllamaProvider(LLMInterface):

    def __init__(self, api_key: str=None, api_url: str=None, 
                 default_input_max_characters: int=1000, 
                 default_generation_max_output_tokens: int=1000,
                 default_generation_temperature: float=0.1):
        
        self.api_key = api_key
        self.api_url = api_url
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None 
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = ollama.Client(
            host=self.api_url if self.api_url and len(self.api_url) else "localhost"
        )

        self.enums = OLLAMAEnums

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def generate_text(self, prompt: str, chat_history: list=[],  max_output_token: int=None, temperature: float=None):

        if not self.client:
            self.logger.error("OLLAMA client was not set")
            return None
        
        if not self.generation_model_id:
            self.logger.error("Generation model for OLLAMA was not set")
            return None
        
        max_output_tokens = max_output_token if max_output_token else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        chat_history.append(self.construct_prompt(prompt=prompt, role=OLLAMAEnums.USER.value))

        response = self.client.chat(
            model=self.generation_model_id,
            messages=chat_history,
            options={
                'temperature': temperature,
                'num_predict': max_output_tokens
            }
        )

        if not response or not response.message or not response.message.content:
            self.logger.error("Error while generating text with OpenAI")
            return None
        
        return response.message.content

    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": prompt
        }
    
    def embed_text(self, text: Union[str, List[str]], document_type: str = None):
        
        if not self.client:
            self.logger.error("Ollama client was not set")
            return None
        
        if isinstance(text, str):
            text = [text]
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for Ollama was not set")
            return None
        
        response = self.client.embed(
            model = self.embedding_model_id,
            input=text,
        )

        if not response or not response["embeddings"] or len(response["embeddings"]) == 0:
            self.logger.error("Error while embedding text with OpenAI")
            return None
        

        # return [rec.embedding for rec in response.embeddings]        
        return response["embeddings"]
    
    