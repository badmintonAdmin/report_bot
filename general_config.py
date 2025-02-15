from dotenv import dotenv_values
import os
from pathlib import Path


class Config:
    def __init__(self):
        values = dotenv_values()
        for key, value in values.items():
            setattr(self, key, value)
        BASE_DIR = Path(__file__).resolve().parent.parent
        DB_PATH = BASE_DIR / self.DATABASE_URL
        self.DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

    def __repr__(self):
        return f"{self.__dict__}"


config = Config()
