from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient

from fastapi import FastAPI
from sqlalchemy.testing.config import db_url

from routers.base import base_router
from routers.data import data_router
from dotenv import load_dotenv
import os
from helpers.config import get_settings
from utils.database_index_setup import setup_database_indexes
import logging

# load_dotenv(".env")

# load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    # Initialize MongoDB client
    app.mongo_conn = AsyncIOMotorClient(settings.DB_URL)
    app.db_client = app.mongo_conn[settings.DB_NAME]

    try:
        yield
    finally:
        # Disconnect MongoDB client
        app.mongo_conn.close()



app = FastAPI(lifespan=lifespan)


@app.get("/")
def welcome():
    return {
        "message": "Hello FASTAPI"
    }


app.include_router(base_router)
app.include_router(data_router)