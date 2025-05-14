from openai import OpenAI
from ..llm_base import LLMBase
import logging
from ..llm_enums import LLMProvider, LLMModelType, DocumentType, OpenAIRoles


class OpenAIDriver(LLMBase):
    """
    Implementation of LLM interface for OpenAI's models.
    Supports both text generation (GPT models) and embedding models.
    """

    def __init__(
        self,
        model_name: str = "gpt-4",
        model_version: str = "turbo",
        api_key: str = None,
        temperature: float = 0.7,
        max_input_tokens: int = 4096,
        max_output_tokens: int = 512
        ):

        super().__init__(
            model_name,
            model_version,
            api_key,
            temperature,
            max_input_tokens,
            max_output_tokens)
        self.provider = LLMProvider.OPENAI.value
        self.api_key = api_key
        self.generation_model = f"{model_name}-{model_version}"
        self.embedding_model = "text-embedding-ada-002"  # Default embedding model

    def _initialize_client(self) -> None:
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=self.api_key)

    def set_generation_model(self, model_version: str):
        """Set the generation model version"""
        if not model_version or not isinstance(model_version, str):
            raise ValueError("Invalid model version. It must be a non-empty string.")
        self.model_version = model_version
        self.generation_model = f"{self.model_name}-{model_version}"

    def set_embedding_model(self, model_version: str):
        """Set the embedding model version"""
        if not model_version or not isinstance(model_version, str):
            raise ValueError("Invalid embedding model version. It must be a non-empty string.")
        self.embedding_model = f"text-embedding-{model_version}"

    def generate_text(
        self,
        user_message: str,
        temperature: float = None,
        max_output_tokens: int = None,
        messages: list[dict] = None
        ):
        """Generate text using OpenAI API
        :param user_message:
        """
        temperature = temperature or self.temperature
        max_output_tokens = max_output_tokens or self.max_output_tokens
        
        if messages:
            try:
                messages.append(self.prepare_message(OpenAIRoles.USER.value, user_message))
                response = self.client.chat.completions.create(
                    model=self.generation_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_output_tokens
                )
                assistant_message = response.choices[0].message.content
                messages.append(self.prepare_message(OpenAIRoles.ASSISTANT.value, assistant_message))
                return assistant_message
            
            except Exception as e:
                logging.error(f"Error in OpenAI text generation. Model: {self.generation_model}, Error: {e}")
                return None
        else:
            return None


    def prepare_history_messages(self, new_message:dict, messages: list[dict]):
        pass

    def prepare_message(self, role: str, content: str):
        return {role: content}


    # def embed_text(self, document_type: str):
    #     """Process text based on document type for embedding"""
    #     if document_type not in [e.value for e in DocumentType]:
    #         raise ValueError(f"Unsupported document type: {document_type}")
    #     return f"Processing {document_type} for OpenAI embedding"
    #
    # def get_embedding(self, text: str):
    #     """Get vector embedding for text"""
    #     try:
    #         response = openai.Embedding.create(
    #             model=self.embedding_model,
    #             input=text
    #         )
    #         return response.data[0].embedding
    #     except Exception as e:
    #         print(f"Error in OpenAI embedding. Model: {self.embedding_model}, Error: {e}")
    #         return None
    #
    # def get_embedding_model(self):
    #     return self.embedding_model
    #
    # def get_generation_model(self):
    #     return self.generation_model
    #
    # def get_model_name(self):
    #     return self.model_name
    #
    # def get_model_version(self):
    #     return self.model_version
    #
    # def get_model_type(self):
    #     return LLMModelType.GENERATION.value