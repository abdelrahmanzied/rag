import string
import random

from helpers.config import Settings, get_settings
import os

class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname((os.path.dirname(__file__)))
        self.file_dir = os.path.join(self.base_dir, "assets/files")

    def generate_random_string(self, length: int=12):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

        # self.app_name = self.settings.APP_NAME
        # self.app_version = self.settings.APP_VERSION
        # self.openai_api_key = self.settings.OPENAI_API_KEY