from fastapi import FastAPI
from routers.base import base_router
from dotenv import load_dotenv

load_dotenv(".env")


app = FastAPI()

@app.get("/")
def welcome():
    return {
        "message": "Hello FASTAPI"
    }

app.include_router(base_router)