from fastapi import APIRouter
import os

base_router = APIRouter(
    prefix="/v1",
    tags=["Health"]
)

@base_router.get('/health')
async def health():
    app_name = os.getenv('APP_NAME')
    app_version = os.getenv('APP_version')
    return {
        'msg': "Hello Worlds from health router",
        'app_name': app_name,
        'app_version': app_version,
    }