from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from helpers.config import get_settings


class BaseDataModel:
    def __init__(self, db_client):
        self.db_client = db_client
        self.app_settings = get_settings()