from typing import Optional, Dict, Any
import anthropic
from ..llm_base import LLMBase
from ..llm_enums import LLMProvider, LLMModelType, DocumentType


class AnthropicDriver(LLMBase):
    """
    Implementation of LLM interface for Anthropic's Claude models.
    """

    AVAILABLE_MODELS = {
        "claude-3-opus": {
            "context_window": 200000,
            "default_tokens": 4096
        },
        "claude-3-sonnet": {
            "context_window": 200000,
            "default_tokens": 4096
        },
        "claude-3-haiku": {
            "context_window": 200000,
            "default_tokens": 4096
        },
        "claude-2.1": {
            "context_window": 100000,
            "default_tokens": 4096
        },
        "claude-2.0": {
            "context_window": 100000,
            "default_tokens": 4096
        }
    }

    def __init__(self, api_key: str, model_name: str = "claude", model_version: str = "3-opus"):
        """
        Initialize Anthropic driver with API key and model configuration.

        Args:
            api_key (str): Anthropic API key
            model_name (str): Base model name (default: "claude")
            model_version (str): Model version (default: "3-opus")
        """
        super().__init__(model_name, model_version)
        self.provider = LLMProvider.ANTHROPIC.value
        self.api_key = api_key
        self.generation_model = f"{model_name}-{model_version}"
        self.embedding_model = None  # Anthropic doesn't currently support embeddings
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Anthropic API client with error handling."""
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Anthropic client: {str(e)}")

    def _validate_model(self, model: str):
        """Validate if the model is supported by Anthropic."""
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
        Set the embedding model version (not currently supported by Anthropic).

        Args:
            model_version (str): Version of the embedding model
        """
        raise NotImplementedError("Anthropic does not currently support embedding models")

    def generate_text(
        self,
        temperature: str = None,
        max_output_tokens: float = None,
        user_message=None,
        messages: int = None
        ) -> Dict[str, Any]:
        """
        Generate text using Anthropic's Claude API.

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
            message = self.client.messages.create(
                model=self.generation_model,
                max_tokens=max_output_tokens,
                temperature=temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return {
                "text": message.content[0].text,
                "model": self.generation_model,
                "finish_reason": message.stop_reason,
                "usage": {
                    "prompt_tokens": message.usage.input_tokens,
                    "completion_tokens": message.usage.output_tokens,
                    "total_tokens": message.usage.input_tokens + message.usage.output_tokens
                }
            }
        except anthropic.APIError as e:
            raise Exception(f"Anthropic API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Text generation failed: {str(e)}")

    def embed_text(self, document_type: str):
        """
        Process text for embedding (not currently supported by Anthropic).

        Args:
            document_type (str): Type of document to embed
        """
        raise NotImplementedError("Anthropic does not currently support text embeddings")

    def get_embedding(self, text: str):
        """
        Get vector embedding for text (not currently supported by Anthropic).

        Args:
            text (str): Text to embed
        """
        raise NotImplementedError("Anthropic does not currently support text embeddings")

    def get_embedding_model(self) -> Optional[str]:
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
            top_p: float = 0.95,):
        self.client.messages.create(
            model=self.generation_model,
            max_tokens=max_output_tokens,
            temperature=temperature,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )
