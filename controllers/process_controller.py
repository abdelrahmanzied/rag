import os

from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .base_controller import BaseController
from .project_controller import ProjectController
from models import ProcessingFileTypes

class ProcessController(BaseController):
    def __init__(self, project_id: str):
        super().__init__()

        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=self.project_id)

    def get_file_type(self, file_name: str):
        file_type = file_name.split('.')[-1]
        return file_type

    def get_file_loader(self, file_name: str):
        file_type = self.get_file_type(file_name=file_name)
        file_path = os.path.join(self.project_path, file_name)

        if file_type == ProcessingFileTypes.TXT.value:
            return TextLoader(file_path=file_path, encoding='utf-8')
        elif file_type == ProcessingFileTypes.PDF.value:
            return PyMuPDFLoader(file_path=file_path)
        else:
            return None

    def get_file_content(self, file_name: str):
        file_loader = self.get_file_loader(file_name=file_name).load()
        print("file_loader:", file_loader)
        if file_loader:
            file_content = [
                rec.page_content
                for rec in file_loader
            ]
            return file_content
        else:
            return None

    def get_file_metadata(self, file_name: str):
        file_loader = self.get_file_loader(file_name=file_name).load()
        if file_loader:
            file_meta_data = [
                rec.metadata
                for rec in file_loader
            ]
            return file_meta_data
        else:
            return None

    def get_file_pages(self, file_name: str):
        file_loader = self.get_file_loader(file_name=file_name)
        if file_loader:
            return file_loader.pages
        else:
            return None

    def process_file_content(
            self,
            file_name: str,
            chunk_size: int = 100,
            overlap_size: int = 20,
    ):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len
        )

        file_content = self.get_file_content(file_name=file_name)
        fime_meta_data = self.get_file_metadata(file_name=file_name)

        chunks = splitter.create_documents(
            file_content,
            metadatas=fime_meta_data
        )

        return chunks