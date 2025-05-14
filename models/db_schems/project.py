from pydantic import BaseModel, Field, field_validator
from typing import Optional
from utils.mongo_encoders import PydanticObjectId, mongo_config


class Project(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    project_id: str = Field(..., min_length=1)

    @field_validator('project_id')
    def validate_project_id(cls, value: str) -> str:
        # Your validation logic here
        return value

    model_config = mongo_config