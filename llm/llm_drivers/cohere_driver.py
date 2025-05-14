import cohere
from typing import Optional, Dict, Any
from ..llm_base import LLMBase
from ..llm_enums import LLMProvider, LLMModelType, DocumentType


class CohereDriver(LLMBase):
    def __init__(self, api_key: str, model_name: str = "command", model_version: str = "latest"):
        super().__init__(model_name, model_version)
        self.client = cohere.Client(api_key)
        self.generation_model = model_name
        self.embedding_model = "embed-english-v3.0"  # Default embedding model

    def set_generation_model(self, model_version: str):
        """Set the generation model version."""
        available_models = {
            "command": "command",
            "command-light": "command-light",
            "command-nightly": "command-nightly",
            "command-r": "command-r"
        }
        if model_version in available_models:
            self.generation_model = available_models[model_version]
        else:
            raise ValueError(f"Unsupported model version: {model_version}")

    def set_embedding_model(self, model_version: str):
        """Set the embedding model version."""
        available_models = {
            "embed-english-v3.0": "embed-english-v3.0",
            "embed-multilingual-v3.0": "embed-multilingual-v3.0"
        }
        if model_version in available_models:
            self.embedding_model = available_models[model_version]
        else:
            raise ValueError(f"Unsupported embedding model: {model_version}")

    def generate_text(
        self,
        temperature: str = None,
        max_output_tokens: float = None,
        user_message=None,
        messages: int = None
        ) -> Dict[str, Any]:
        """Generate text using Cohere's generation API.
        :param user_message:
        """
        try:
            response = self.client.generate(
                model=self.generation_model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_output_tokens,
                p=top_p,
                k=top_k,
                frequency_penalty=repetition_penalty,
                return_likelihoods='NONE'
            )

            return {
                "text": response.generations[0].text,
                "tokens_used": response.tokens,
                "model": self.generation_model
            }
        except Exception as e:
            raise Exception(f"Text generation failed: {str(e)}")

    def embed_text(self, texts: list[str], document_type: str = DocumentType.TEXT.value) -> Dict[str, Any]:
        """Embed multiple texts using Cohere's embedding API."""
        try:
            response = self.client.embed(
                texts=texts,
                model=self.embedding_model,
                input_type=document_type
            )

            return {
                "embeddings": response.embeddings,
                "tokens": response.meta['billed_tokens'],
                "model": self.embedding_model
            }
        except Exception as e:
            raise Exception(f"Text embedding failed: {str(e)}")

    def get_embedding(self, text: str) -> list[float]:
        """Get embedding for a single text."""
        try:
            response = self.embed_text([text])
            return response["embeddings"][0]
        except Exception as e:
            raise Exception(f"Single text embedding failed: {str(e)}")

    def get_embedding_model(self) -> str:
        return self.embedding_model

    def get_generation_model(self) -> str:
        return self.generation_model

    def get_model_name(self) -> str:
        return self.model_name

    def get_model_version(self) -> str:
        return self.model_version

    def get_model_type(self) -> str:
        return LLMProvider.COHERE.value
