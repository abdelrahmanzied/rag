# models/file_model.py
from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId


class File(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    project_id: str = Field(..., min_length=1)
    file_name: str
    file_path: str
    metadata: Optional[dict] = {}

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return self.model_dump(exclude_none=True)