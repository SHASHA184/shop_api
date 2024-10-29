from dotenv import load_dotenv
import os

load_dotenv()

DEFAULT_USER = os.getenv('DEFAULT_USER')
DEFAULT_HOST = os.getenv('DEFAULT_HOST')
DEFAULT_DB = os.getenv('DEFAULT_DB')
DEFAULT_PASSWORD = os.getenv('DEFAULT_PASSWORD')
DEFAULT_PORT = os.getenv('DEFAULT_PORT')

DATABASE_URL = f'postgresql+asyncpg://{DEFAULT_USER}:{DEFAULT_PASSWORD}@{DEFAULT_HOST}:{DEFAULT_PORT}/{DEFAULT_DB}'