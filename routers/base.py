from fastapi import APIRouter, Depends
import os

from helpers.config import Settings, get_settings

base_router = APIRouter(
    prefix="/v1",
    tags=["Health"]
)

@base_router.get('/health')
async def health(app_settings: Settings = Depends(get_settings)):
    return {
        'msg': "Hello Worlds from health router",
        'app_name': app_settings.APP_NAME,
        'app_version': app_settings.APP_VERSION,
    }
