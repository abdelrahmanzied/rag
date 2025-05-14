from models.enums.db_collections import Collections
import logging
from pymongo.errors import OperationFailure

logger = logging.getLogger(__name__)


async def list_existing_indexes(db_client):
    """
    List all existing indexes for each collection.

    This function is useful for debugging and understanding the current state
    of indexes in your MongoDB database.
    """
    logger.info("Checking existing indexes in the database...")
    for collection_enum in Collections:
        collection = db_client[collection_enum.value]
        indexes = await collection.index_information()
        logger.info(f"Indexes for {collection_enum.value}: {indexes}")


async def create_index_safely(collection, keys, **kwargs):
    """
    Helper function to create an index and handle existing index errors.

    This function attempts to create an index and gracefully handles the case
    where an index on the same keys already exists with a different name.

    Args:
        collection: MongoDB collection object
        keys: List of tuples defining index keys and directions
        **kwargs: Additional index options (like unique, background, etc.)
    """
    try:
        await collection.create_index(keys, **kwargs)
        logger.info(f"Created index {kwargs.get('name')} on {collection.name}")
    except OperationFailure as e:
        if "Index already exists with a different name" in str(e):
            # Extract the existing index name from the error message if possible
            error_msg = str(e)
            existing_index_name = error_msg.split("Index already exists with a different name: ")[1].split(",")[
                0] if ":" in error_msg else "unknown"

            logger.info(
                f"Index on {keys} already exists with name '{existing_index_name}' in {collection.name}. Keeping existing index.")
        else:
            logger.error(f"Failed to create index {kwargs.get('name')} on {collection.name}: {str(e)}")
            raise


async def rename_index(collection, old_name, new_keys, **new_options):
    """
    Drop old index and create a new one with the desired name.

    This function is useful when you want to standardize index naming without
    losing the benefits of existing indexes.

    Warning: Dropping and recreating indexes can be performance-intensive on large collections.
    Consider running this during maintenance windows for production systems.

    Args:
        collection: MongoDB collection object
        old_name: Name of the existing index to drop
        new_keys: List of tuples defining index keys and directions for the new index
        **new_options: Additional index options for the new index
    """
    try:
        # First create the new index
        await collection.create_index(new_keys, **new_options)
        logger.info(f"Created new index {new_options.get('name')} on {collection.name}")

        # Then drop the old one
        await collection.drop_index(old_name)
        logger.info(f"Successfully dropped old index {old_name} on {collection.name}")
    except Exception as e:
        logger.error(f"Failed to rename index {old_name} to {new_options.get('name')}: {str(e)}")
        raise


async def setup_database_indexes(db_client):
    """
    Set up all required indexes for the application database.
    Should be called during application startup.

    This function ensures all required indexes exist, either by creating them
    or by keeping track of existing ones with different names.
    """
    try:
        # First, list all existing indexes for diagnostic purposes
        await list_existing_indexes(db_client)

        # Projects collection
        await create_index_safely(
            db_client[Collections.PROJECT_COLLECTION.value],
            [("project_id", 1)],
            unique=True,
            background=True,
            name="idx_project_id"
        )

        # Chunks collection
        await create_index_safely(
            db_client[Collections.CHUNK_COLLECTION.value],
            [("project_id", 1)],
            background=True,
            name="idx_chunk_project_id"
        )

        await create_index_safely(
            db_client[Collections.CHUNK_COLLECTION.value],
            [("file_id", 1)],
            background=True,
            name="idx_chunk_file_id"
        )

        await create_index_safely(
            db_client[Collections.CHUNK_COLLECTION.value],
            [("project_id", 1), ("file_id", 1)],
            background=True,
            name="idx_chunk_project_file"
        )

        await create_index_safely(
            db_client[Collections.CHUNK_COLLECTION.value],
            [("file_id", 1), ("chunk_order", 1)],
            background=True,
            name="idx_chunk_file_order"
        )

        # Files collection
        await create_index_safely(
            db_client[Collections.FILE_COLLECTION.value],
            [("project_id", 1)],
            background=True,
            name="idx_file_project_id"
        )

        await create_index_safely(
            db_client[Collections.FILE_COLLECTION.value],
            [("project_id", 1), ("file_name", 1)],
            unique=True,
            background=True,
            name="idx_file_project_name"
        )

        logger.info("All database indexes have been set up successfully")

        # For verification, list indexes again after setup
        await list_existing_indexes(db_client)
    except Exception as e:
        logger.error(f"Failed to set up database indexes: {str(e)}")
        raise


# Optional function to be called explicitly when index renaming is desired
async def standardize_index_names(db_client):
    """
    Standardize index names according to naming convention.

    This is an optional maintenance function that can be called to rename
    automatically generated indexes to follow your naming convention.

    Warning: This should be run during maintenance windows for production systems.
    """
    try:
        # Example: If you detect an automatically created index named 'project_id_1'
        # that should be named 'idx_project_id'
        indexes = await db_client[Collections.PROJECT_COLLECTION.value].index_information()

        # Check if the auto-generated index exists and our preferred name doesn't
        if 'project_id_1' in indexes and 'idx_project_id' not in indexes:
            await rename_index(
                db_client[Collections.PROJECT_COLLECTION.value],
                'project_id_1',
                [("project_id", 1)],
                unique=True,
                background=True,
                name="idx_project_id"
            )

        # Add more standardization as needed for other collections

        logger.info("Index name standardization completed")
    except Exception as e:
        logger.error(f"Failed to standardize index names: {str(e)}")
        raise