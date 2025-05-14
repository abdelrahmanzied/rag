# models/file_model.py
from models.base_data_model import BaseDataModel
from models.chunk_model import ChunkModel
from models.enums.db_collections import Collections
from bson import ObjectId
from typing import List, Dict, Any


class FileModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = db_client[Collections.FILE_COLLECTION.value]

    async def insert_file(self, file_data: dict) -> dict:
        result = await self.collection.insert_one(file_data)
        return {"id": str(result.inserted_id)}

    async def get_file_chunks(self, file_id: str):
        # Get all chunks associated with this file
        chunk_model = ChunkModel(self.db_client)
        return await chunk_model.get_chunks_by_file_id(file_id)

    def _serialize_mongo_doc(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert MongoDB document with ObjectId to JSON-serializable dict.
        """
        if not doc:
            return doc

        result = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, dict):
                result[key] = self._serialize_mongo_doc(value)
            elif isinstance(value, list):
                result[key] = [
                    self._serialize_mongo_doc(item) if isinstance(item, dict)
                    else str(item) if isinstance(item, ObjectId)
                    else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    async def get_project_files(self, project_id: str):
        cursor = self.collection.find({"project_id": project_id})
        documents = await cursor.to_list(length=None)

        # Serialize MongoDB documents to make them JSON-serializable
        serialized_documents = [self._serialize_mongo_doc(doc) for doc in documents]
        return serialized_documents
