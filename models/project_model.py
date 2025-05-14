from .base_data_model import BaseDataModel
from .enums.db_collections import Collections
from .db_schems.project import Project


class ProjectModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[Collections.PROJECT_COLLECTION.value]

    async def create_project(self, project: Project):
        result = await self.collection.insert_one(project.model_dump())
        project._id = result.inserted_id
        return project

    async def get_project_or_create(self, project_id: str):
        # Access the collection properly first
        # collection = self.db_client[Collections.PROJECT_COLLECTION.value]
        # Then use find_one
        record = await self.collection.find_one({"project_id": project_id})
        if record:
            return Project(**record)
        else:
            project = Project(project_id=project_id)
            result = await self.create_project(project=project)
            return result

    async def get_all_projects(
            self,
            page_size: int = 10,
            page_number: int = 1,
    ):
        """
        Retrieve a list of all project records from the database, paginated by page size and number.
    
        :param page_size: The number of projects to retrieve per page (default: 10).
        :param page_number: The page number to retrieve data from (default: 1).
        :return: A list of Project instances representing the retrieved project records.
        """
        total_records = await self.collection.count_documents({})
        total_pages = (total_records + page_size - 1) // page_size

        records_cursor = self.collection.find().skip((page_number - 1) * page_size).limit(page_size)

        records = await records_cursor.to_list(length=page_size)
        projects = [Project(**record) for record in records]
        return projects, total_pages

