import os

from fastapi import UploadFile

from .project_controller import ProjectController
from .base_controller import BaseController
from models import ResponseSignal, ProcessRequest
import re

class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.file_allowed_types = ['text/plain', 'application/pdf']
        self.file_max_size = 10485760  # 10 MB

    async def validate_uploaded_file(
            self,
            file: UploadFile
    ):
        # return False
        if file.content_type not in self.file_allowed_types:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        elif file.size > self.file_max_size:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value
        else:
            return True, ResponseSignal.FILE_VALID.value

    def generate_unique_file_path(
            self,
            org_file_name: str,
            project_id: str
    ):
        random_id = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)
        cleaned_file_name = self.clean_file_name(org_file_name)
        unique_file_name = f"{random_id}_{cleaned_file_name}"
        unique_file_path = os.path.join(project_path, unique_file_name)

        while os.path.exists(unique_file_path):
            random_id = self.generate_random_string()
            unique_file_name = f"{random_id}_{cleaned_file_name}"
            unique_file_path = os.path.join(project_path, unique_file_name)

        return os.path.join(project_path, unique_file_name), unique_file_name

    def clean_file_name(
            self,
            file_name: str
    ):
        cleaned_file_name = re.sub(r"[^a-zA-Z0-9_.-]", "", file_name)
        cleaned_file_name = cleaned_file_name.replace(" ", "_")
        return cleaned_file_name