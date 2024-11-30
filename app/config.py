from dotenv import load_dotenv
import os

load_dotenv()

DEFAULT_USER = os.getenv('DEFAULT_USER', 'postgres')
DEFAULT_HOST = os.getenv('DEFAULT_HOST', 'db')
DEFAULT_DB = os.getenv('DEFAULT_DB', 'shop_db')
DEFAULT_PASSWORD = os.getenv('DEFAULT_PASSWORD', 'postgres')
DEFAULT_PORT = os.getenv('DEFAULT_PORT', 5432)

DATABASE_URL = f'postgresql+asyncpg://{DEFAULT_USER}:{DEFAULT_PASSWORD}@{DEFAULT_HOST}:{DEFAULT_PORT}/{DEFAULT_DB}'

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30