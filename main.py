from fastapi import FastAPI
from routers.base import base_router
from dotenv import load_dotenv
import os

# load_dotenv(".env")

# load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = FastAPI()

@app.get("/")
def welcome():
    return {
        "message": "Hello FASTAPI"
    }

app.include_router(base_router)