from typing import Dict, Any, List, Optional
import mistralai
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from ..llm_base import LLMBase
from ..llm_enums import LLMProvider, LLMModelType, DocumentType


class MistralDriver(LLMBase):
    """
    Implementation of LLM interface for Mistral AI models.
    """

    AVAILABLE_MODELS = {
        "mistral-tiny": {
            "context_window": 32768,
            "default_tokens": 4096
        },
        "mistral-small": {
            "context_window": 32768,
            "default_tokens": 4096
        },
        "mistral-medium": {
            "context_window": 32768,
            "default_tokens": 4096
        },
        "mistral-large": {
            "context_window": 32768,
            "default_tokens": 4096
        }
    }

    EMBEDDING_MODELS = {
        "mistral-embed": {
            "dimensions": 1024,
            "max_input_tokens": 8192
        }
    }

    def __init__(self, api_key: str, model_name: str = "mistral", model_version: str = "small"):
        """
        Initialize Mistral driver with API key and model configuration.
        
        Args:
            api_key (str): Mistral API key
            model_name (str): Base model name (default: "mistral")
            model_version (str): Model version (default: "small")
        """
        super().__init__(model_name, model_version)
        self.provider = LLMProvider.MISTRAL.value
        self.api_key = api_key
        self.generation_model = f"{model_name}-{model_version}"
        self.embedding_model = "mistral-embed"
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Mistral API client with error handling."""
        try:
            self.client = MistralClient(api_key=self.api_key)
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Mistral client: {str(e)}")

    def _validate_model(self, model: str):
        """Validate if the model is supported by Mistral."""
        if model not in self.AVAILABLE_MODELS:
            raise ValueError(
                f"Unsupported model: {model}. Available models: {list(self.AVAILABLE_MODELS.keys())}"
            )

    def set_generation_model(self, model_version: str):
        """
        Set the generation model version.
        
        Args:
            model_version (str): Version of the model to use
        """
        full_model_name = f"{self.model_name}-{model_version}"
        self._validate_model(full_model_name)
        self.model_version = model_version
        self.generation_model = full_model_name

    def set_embedding_model(self, model_version: str):
        """
        Set the embedding model version.
        
        Args:
            model_version (str): Version of the embedding model
        """
        if model_version not in self.EMBEDDING_MODELS:
            raise ValueError(f"Unsupported embedding model: {model_version}")
        self.embedding_model = model_version

    def generate_text(
        self,
        temperature: str = None,
        max_output_tokens: float = None,
        user_message=None,
        messages: int = None
        ) -> Dict[str, Any]:
        """
        Generate text using Mistral's API.
        
        Args:
            prompt (str): Input prompt for generation
            temperature (float): Controls randomness in generation
            max_output_tokens (int): Maximum number of tokens to generate
            top_p (float): Nucleus sampling parameter
            top_k (int): Top-k sampling parameter
            repetition_penalty (float): Penalty for token repetition

        Returns:
            Dict[str, Any]: Response containing generated text and metadata
            :param user_message:
        """
        try:
            messages = [
                ChatMessage(role="user", content=prompt)
            ]

            response = self.client.chat(
                model=self.generation_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_output_tokens,
                top_p=top_p,
                random_seed=None,  # Let API choose random seed
            )

            return {
                "text": response.choices[0].message.content,
                "model": self.generation_model,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            raise Exception(f"Text generation failed: {str(e)}")

    def embed_text(self, texts: List[str], document_type: str = DocumentType.TEXT.value) -> Dict[str, Any]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts (List[str]): List of texts to embed
            document_type (str): Type of document being embedded

        Returns:
            Dict[str, Any]: Dictionary containing embeddings and metadata
        """
        try:
            response = self.client.embeddings(
                model=self.embedding_model,
                inputs=texts
            )

            return {
                "embeddings": [emb.embedding for emb in response.data],
                "model": self.embedding_model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            raise Exception(f"Text embedding failed: {str(e)}")

    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a single text.
        
        Args:
            text (str): Text to embed

        Returns:
            List[float]: Vector embedding
        """
        try:
            response = self.embed_text([text])
            return response["embeddings"][0]
        except Exception as e:
            raise Exception(f"Single text embedding failed: {str(e)}")

    def get_embedding_model(self) -> str:
        """Get the current embedding model name."""
        return self.embedding_model

    def get_generation_model(self) -> str:
        """Get the current generation model name."""
        return self.generation_model

    def get_model_name(self) -> str:
        """Get the base model name."""
        return self.model_name

    def get_model_version(self) -> str:
        """Get the current model version."""
        return self.model_version

    def get_model_type(self) -> str:
        """Get the model type."""
        return LLMModelType.GENERATION.value

    def get_model_context_window(self) -> int:
        """Get the context window size for the current model."""
        return self.AVAILABLE_MODELS[self.generation_model]["context_window"]

    def chat_stream(
            self,
            prompt: str,
            temperature: float = 0.7,
            max_output_tokens: int = 512,
            top_p: float = 0.95,
    ) -> Iterator[str]:
        """
        Stream chat responses from Mistral.
        
        Args:
            prompt (str): Input prompt
            temperature (float): Temperature parameter
            max_output_tokens (int): Maximum tokens to generate
            top_p (float): Top-p sampling parameter

        Yields:
            Iterator[str]: Stream of generated text chunks
        """
        try:
            messages = [
                ChatMessage(role="user", content=prompt)
            ]

            stream = self.client.chat_stream(
                model=self.generation_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_output_tokens,
                top_p=top_p,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise Exception(f"Streaming chat failed: {str(e)}")