from typing import Optional, Dict, Any, List
import google.generativeai as genai
from ..llm_base import LLMBase
import functools

from ..llm_enums import LLMProvider


class GoogleDriver(LLMBase):
    """Driver class for Google's Gemini AI API with enhanced features"""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini",
        model_version: str = "2.0-flash",
        temperature: float = 0.7,
        max_input_tokens: int = 30000,
        max_output_tokens: int = 2048
    ):
        """
        Initialize the Google Gemini driver with the specified parameters
        """
        super().__init__(
            model_name=model_name,
            model_version=model_version,
            api_key=api_key,
            temperature=temperature,
            max_input_tokens=max_input_tokens,
            max_output_tokens=max_output_tokens
        )
        self.generation_model = "gemini-2.0-flash"
        self.provider = LLMProvider.GOOGLE.value

    def _initialize_client(self):
        """
        Initializes the client with the specified configuration.

        Sets up the GenerativeModel client using the provided API key and model name.
        This method configures the client and prepares it for usage.

        :rtype: None
        """
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(
            model_name=self.model_name,
        )

    @property
    async def available_models(self) -> list[str]:
        """Get list of available Gemini models"""
        try:
            models = genai.list_models()
            return [model.name for model in models if "gemini" in model.name]
        except Exception as e:
            print(f"Error fetching available models: {str(e)}")
            return []

    def set_generation_model(self, model_version: str):
        """Set a new generation model version"""
        self.model_version = model_version
        new_model = f"{self.model_name}-{model_version}"
        if new_model in self.available_models:
         self.generation_model= f"{self.model_name}-{model_version}"

    def set_embedding_model(self, model_version: str):
        """Set embedding model - Currently not supported in Gemini"""
        raise NotImplementedError("Embedding models are not yet supported in Gemini API")

    @functools.lru_cache(maxsize=128)
    def _create_chat_session(self):
        """Create a new chat session with caching"""

        return self.client.start_chat(history=[])

    async def generate_text(
        self,
        user_message: str,
        temperature: float = None,
        max_output_tokens: int = None,
        messages: list[dict] = None
    ) -> Dict[str, Any]:
        """
        """
        try:
            # Create new chat session
            chat = self._create_chat_session()

            # Update configuration if needed
            if temperature is not None or max_output_tokens is not None:
                generation_config = {
                    "temperature": temperature if temperature is not None else self.temperature,
                    "max_output_tokens": max_output_tokens if max_output_tokens is not None else self.max_output_tokens,
                }
                chat.model.generation_config.update(generation_config)

            # Handle history if provided
            if messages:
                for msg in messages:
                    prepared_msg = self.prepare_message(msg["role"], msg["content"])
                    chat.send_message(prepared_msg["content"])

            # Send message and get response using Flash2 API
            response = await chat.send_message_async(user_message)

            return {
                "text": response.text,
                "model": self.model_name,
                "usage": {
                    "prompt_tokens": getattr(response, "prompt_token_count", None),
                    "completion_tokens": getattr(response, "candidates_token_count", None),
                    "total_tokens": None
                },
                "finish_reason": getattr(response, "finish_reason", None)
            }

        except Exception as e:
            return {
                "error": str(e),
                "text": None,
                "model": self.model_name,
                "usage": None,
                "finish_reason": "error"
            }

    def prepare_history_messages(self, new_message: dict, messages: list[dict]) -> List[Dict[str, str]]:
        """Prepare chat history messages"""
        prepared_messages = []
        for message in messages + [new_message]:
            if message.get("role") in ["user", "assistant"]:
                prepared_messages.append(
                    self.prepare_message(
                        message["role"],
                        message.get("content", "")
                    ))
        return prepared_messages

    def prepare_message(self, role: str, content: str) -> Dict[str, str]:
        """Prepare a single message with role and content"""
        return {
            "role": role,
            "content": content
        }
