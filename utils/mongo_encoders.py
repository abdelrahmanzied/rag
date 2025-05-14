from bson import ObjectId
from pydantic import ConfigDict
from pydantic_core import core_schema
from typing import Annotated, Any, Dict


class PyObjectId:
    """
    Custom type for handling MongoDB ObjectIds in Pydantic models.
    """

    @classmethod
    def __get_pydantic_core_schema__(
            cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        """
        Define the schema for validating and serializing ObjectId.
        """
        return core_schema.union_schema([
            # Handle actual ObjectId objects
            core_schema.is_instance_schema(ObjectId),
            # Handle string representation of ObjectId
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(
                    lambda s: ObjectId(s) if ObjectId.is_valid(s) else s
                ),
            ]),
        ],
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda obj: str(obj) if isinstance(obj, ObjectId) else obj
            ))


# Type annotation for ObjectId fields in Pydantic models
PydanticObjectId = Annotated[str, PyObjectId]


def serialize_mongo_doc(doc: Dict) -> Dict:
    """
    Convert MongoDB document with ObjectId to JSON-serializable dict.
    """
    if isinstance(doc, dict):
        for key, value in list(doc.items()):
            if isinstance(value, ObjectId):
                doc[key] = str(value)
            elif isinstance(value, dict):
                doc[key] = serialize_mongo_doc(value)
            elif isinstance(value, list):
                doc[key] = [
                    serialize_mongo_doc(item) if isinstance(item, dict)
                    else str(item) if isinstance(item, ObjectId)
                    else item
                    for item in value
                ]
    return doc


# Pydantic model config for MongoDB documents
mongo_config = ConfigDict(
    arbitrary_types_allowed=True,
    populate_by_name=True,
    json_schema_extra={
        "example": {
            "_id": "507f1f77bcf86cd799439011",
            "project_id": "my-project"
        }
    }
)