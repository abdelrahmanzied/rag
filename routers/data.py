import aiofiles
from fastapi import APIRouter, Depends, UploadFile, status
import os
import logging

from fastapi.responses import JSONResponse

from helpers.config import Settings, get_settings
from controllers import DataController, ProjectController
from models import ResponseSignal

logger = logging.getLogger('fastapi')
app_settings = get_settings()

data_router = APIRouter(
    prefix="/v1/data",
    tags=["Health"]
)

@data_router.get('/health')
async def data_health():
    return {
        'msg': "Hello data_health",

    }


@data_router.post("/upload/{project_id}")
async def upload_file(
        project_id: str,
        file: UploadFile,
):
    data_controller = DataController()

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

    return JSONResponse(
        content={
            "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_name": file_name,
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
