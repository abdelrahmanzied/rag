from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from utils.mongo_encoders import PydanticObjectId, mongo_config


class Chunk(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    project_id: str = Field(..., min_length=1)
    file_id: str = Field(..., min_length=1)
    chunk_content: str
    chunk_metadata: Dict[str, Any]
    chunk_order: int = Field(..., gt=0)

    model_config = mongo_config

    def to_dict(self) -> dict:
        """
        Convert the Chunk object's data to a dictionary format.
        """
        return self.model_dump(exclude_none=True)