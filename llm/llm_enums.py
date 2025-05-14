from enum import Enum


class LLMProvider(Enum):
    """
    An enumeration for various LLM providers.
    """
    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    HUGGING_FACE = "hugging_face"


class LLMModelType(Enum):
    """
    An enumeration for different types of LLM models.
    """
    GENERATION = "generation"
    EMBEDDING = "embedding"


class OpenAIRoles(Enum):
    """
    An enumeration for OpenAI roles.
    """
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class DocumentType(Enum):
    """
    An enumeration for document types for embedding.
    """
    TEXT = "text"
    HTML = "html"
    PDF = "pdf"
    DOCX = "docx"