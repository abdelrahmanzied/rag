from abc import ABC, abstractmethod


class LLMBase(ABC):
    
    def __init__(
            self,
            model_name: str,
            model_version: str,
            api_key: str,

            temperature: float = 0.7,
            max_input_tokens: int = 2048,
            max_output_tokens: int = 512
    ):
        """
        Initializes the LLMBase model.
    
        Args:
            model_name (str): The name of the language model.
            model_version (str): The version of the language model.
            api_key (str): The API key used for authentication.
            temperature (float): The sampling temperature for text generation.
            max_input_tokens (int): The maximum number of input tokens.
            max_output_tokens (int): The maximum number of output tokens.
        """
        self.model_name = model_name
        self.model_version = model_version
        self.api_key = api_key
        self.temperature = temperature
        self.max_input_tokens = max_input_tokens
        self.max_output_tokens = max_output_tokens
        self._initialize_client()

    @abstractmethod
    def _initialize_client(self):
        """Initialize the provider-specific client. Must be implemented by subclasses."""
        pass

    @property
    @abstractmethod
    async def available_models(self) -> list[str]:
        pass

    @abstractmethod
    def set_generation_model(self, model_version: str):
        """
        Sets the generation model version.
    
        Args:
            model_version (str): The version of the generation model to be set.
        """
        pass

    @abstractmethod
    def set_embedding_model(self, model_version: str):
        """
        Sets the embedding model version.
    
        Args:
            model_version (str): The version of the embedding model to be set.
        """
        pass

    @abstractmethod
    def generate_text(
            self,
            user_message: str,
            temperature: float = None,
            max_output_tokens: int = None,
            messages: list[dict] = None
            # top_p: float = 0.95,
            # top_k: int = 50,
            # repetition_penalty: float = 1.1,
    ):
        """
        Generates text using specified parameters and messages.

        Args:
            temperature (float): Controls randomness. Higher values generate 
                more random outputs. Defaults to the class-level temperature.
            max_output_tokens (int): Maximum tokens in the generated output. 
                Defaults to the class-level max_output_tokens.
            messages (list[dict]): List of prompt messages for text generation.

        Returns:
            str: Generated text based on the provided prompts and parameters.
            :param user_message:
        """
        temperature = temperature if temperature is not None else self.temperature
        max_output_tokens = max_output_tokens if max_output_tokens is not None else self.max_output_tokens
        pass

    @abstractmethod
    def prepare_history_messages(self, new_message: dict, messages: list[dict]):
        pass


    @abstractmethod
    def prepare_message(self, role: str, content: str):
        pass

    # @abstractmethod
    # def embed_text(self, document_type: str):
    #     """
    #     Embeds text based on the specified document type.
    #
    #     Args:
    #         document_type (str): The type of document to embed.
    #     """
    #     pass
    #
    # @abstractmethod
    # def get_embedding(self, text: str):
    #     """
    #     Retrieves the embedding for the given text.
    #
    #     Args:
    #         text (str): The text for which to generate an embedding.
    #     """
    #     pass
    #
    # @abstractmethod
    # def get_embedding_model(self):
    #     """
    #     Returns the name or details of the current embedding model.
    #     """
    #     pass
    #
    # @abstractmethod
    # def get_generation_model(self):
    #     """
    #     Returns the name or details of the current generation model.
    #     """
    #     pass
    #
    # @abstractmethod
    # def get_model_name(self):
    #     """
    #     Returns the name of the model.
    #
    #     Returns:
    #         str: The name of the model.
    #     """
    #     pass
    #
    # @abstractmethod
    # def get_model_version(self):
    #     """
    #     Returns the version of the model.
    #
    #     Returns:
    #         str: The version of the model.
    #     """
    #     pass
    #
    # @abstractmethod
    # def get_model_type(self):
    #     """
    #     Returns the type of the model (e.g., generation or embedding).
    #
    #     Returns:
    #         str: The type of the model.
    #     """
    #     pass
    #
    #
