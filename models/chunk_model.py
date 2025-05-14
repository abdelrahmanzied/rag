from uuid import UUID
from bson.objectid import ObjectId
from langchain_core.documents import Document

from models.base_data_model import BaseDataModel
from models.db_schems import Chunk
from models.enums.db_collections import Collections



class ChunkModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = db_client[Collections.CHUNK_COLLECTION.value]

    async def insert_chunk(
            self,
            project_id: str,
            file_id: str,
            chunk_data: list[Document],
            batch_size: int = 100
    ) -> dict:
        """
        Inserts multiple document chunks into the database in batches. This asynchronous
        function processes a list of document chunks, structures them properly, and performs
        bulk insertion using the specified batch size. It ensures each chunk is annotated
        with an order before insertion.

        :param project_id: The ID of the project associated with the document chunks.
        :param file_id: The ID of the file these document chunks are a part of.
        :param chunk_data: A list of `Document` objects representing the document chunks.
        :param batch_size: The size of each batch for bulk insertion. Defaults to 100.
        :return: A dictionary containing the number of successfully inserted chunks
            and the total number of chunks processed.
        :rtype: dict
        """
        if not chunk_data:
            return {"success_count": 0, "total_count": 0}

        inserted_ids = []
        total_chunks = len(chunk_data)

        for i in range(0, total_chunks, batch_size):
            chunk_batch = chunk_data[i:i + batch_size]
            chunk_docs = []

            for idx, chunk in enumerate(chunk_batch):
                # Create a proper Chunk object with all required fields
                chunk_obj = Chunk(
                    project_id=project_id,
                    file_id=file_id,
                    chunk_content=chunk.page_content,
                    chunk_metadata=chunk.metadata,
                    chunk_order=idx + 1  # Adding required chunk_order field
                ).to_dict()
                chunk_docs.append(chunk_obj)

            # Insert the batch and collect IDs
            
            result = await self.collection.insert_many(chunk_docs)
            inserted_ids.extend(result.inserted_ids)

        # Return a simple dictionary without any coroutine objects
        return {
            "success_count": len(inserted_ids),
            "total_count": total_chunks,
        }

    async def get_chunk_by_id(self, chunk_id: UUID) -> dict:
        """
        Retrieve a single chunk by its unique ID.
        """
        chunk = await self.collection.find_one({"_id": ObjectId(str(chunk_id))})
        return chunk

    async def update_chunk(self, chunk_id: UUID, update_data: dict) -> int:
        """
        Update a chunk's data in the database.

        :param chunk_id: The UUID of the chunk to update.
        :param update_data: A dictionary with the fields to update.
        :return: The count of modified documents.
        """
        result = await self.collection.update_one({"_id": ObjectId(str(chunk_id))}, {"$set": update_data})
        return result.modified_count

    async def delete_chunk(self, chunk_id: UUID) -> int:
        """
        Delete a chunk from the database.
    
        :param chunk_id: The UUID of the chunk to delete.
        :return: The count of deleted documents.
        """
        result = await self.collection.delete_one({"_id": ObjectId(str(chunk_id))})
        return result.deleted_count

    async def delete_chunks_by_project_id(self, project_id: str) -> int:
        """
        Delete all chunks associated with a specific project.
    
        :param project_id: The project ID whose chunks are to be deleted.
        :return: The count of deleted documents.
        """
        result = await self.collection.delete_many({"project_id": project_id})
        return result.deleted_count

    async def get_chunks_by_project_id(self, project_id: str) -> list:
        """
        Get all chunks related to a specific project.

        :param project_id: The project ID to filter chunks by.
        :return: A list of chunks as dictionaries.
        """
        cursor = self.collection.find({"project_id": project_id})
        return await cursor.to_list(length=None)

    # In models/chunk_model.py
    async def get_chunks_by_file_id(self, file_id: str) -> list:
        """
        Get all chunks related to a specific file.

        :param file_id: The file ID to filter chunks by.
        :return: A list of chunks as dictionaries.
        """
        cursor = self.collection.find({"file_id": file_id})
        return await cursor.to_list(length=None)
