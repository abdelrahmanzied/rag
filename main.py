from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient

from fastapi import FastAPI
from routers.base import base_router
from routers.data import data_router
from dotenv import load_dotenv
import os
from helpers.config import get_settings


# load_dotenv(".env")

# load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    # Initialize MongoDB client
    client = AsyncIOMotorClient(settings.DB_URL)
    app.state.db = client[settings.DB_NAME]
    try:
        yield
    finally:
        # Disconnect MongoDB client
        client.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def welcome():
    return {
        "message": "Hello FASTAPI"
    }

app.include_router(base_router)
app.include_router(data_router)