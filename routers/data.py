from urllib import request

import aiofiles
from fastapi import APIRouter, Depends, UploadFile, status, Request
import os
import logging

from fastapi.responses import JSONResponse

from helpers.config import Settings, get_settings
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal, ProcessRequest
from langchain_community.document_loaders import TextLoader

from models.chunk_model import ChunkModel
from models.file_model import FileModel
from models.project_model import ProjectModel

logger = logging.getLogger('fastapi')
app_settings = get_settings()

data_router = APIRouter(
    prefix="/v1/data",
    tags=["Health"]
)

@data_router.get('/health')
async def data_health():
    return {
        'msg': "Hello data_router health",
    }


@data_router.post("/upload/{project_id}")
async def upload_file(
        request: Request,
        project_id: str,
        file: UploadFile,
        app_settings: Settings = Depends(get_settings),
):
    data_controller = DataController()
    project_model = ProjectModel(
        db_client=request.app.db_client,
    )

    project = await project_model.get_project_or_create(
        project_id=project_id)

    is_valid, msg = await data_controller.validate_uploaded_file(file=file)

    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path, file_name = data_controller.generate_unique_file_path(
        org_file_name=file.filename,
        project_id=project_id
    )

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error while uploading file: {e}")
        return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    file_model = FileModel(db_client=request.app.db_client)
    file_record = await file_model.insert_file({
        "project_id": project_id,
        "file_name": file_name,
        "file_path": file_path,
        "metadata": {
            "original_name": file.filename,
            "content_type": file.content_type
        }
    })

    return JSONResponse(
        content={
            "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_name": file_name,
            "file_id": file_record["id"]
        }
    )

    # if is_valid:
    #     return JSONResponse(
    #         content={
    #             'msg': msg,
    #             'is_valid': is_valid
    #         },
    #     )
    # else:
    #     return JSONResponse(
    #         content={
    #             'msg': msg,
    #             'is_valid': is_valid
    #         },
    #         status_code=status.HTTP_400_BAD_REQUEST
    #     )


@data_router.post("/process/{project_id}")
async def process_file(
        request: Request,
        project_id: str,
        process_request: ProcessRequest
):
    process_controller = ProcessController(project_id=project_id)
    file_chunks = process_controller.process_file_content(
        file_name=process_request.file_id,
        chunk_size=process_request.chunk_size,
        overlap_size=process_request.overlap_size
    )

    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_PROCESSING_FAILED.value
            }
        )

    chunk_model = ChunkModel(db_client=request.app.db_client)
    inserted_chunks = await chunk_model.insert_chunk(
        project_id=project_id,
        file_id=process_request.file_id,
        chunk_data=file_chunks,
        # batch_size=process_request.batch_size
    )

    return inserted_chunks

@data_router.get("/files/{project_id}")
async def get_project_files(project_id: str, request: Request):
    file_model = FileModel(db_client=request.app.db_client)
    files = await file_model.get_project_files(project_id=project_id)
    return files

