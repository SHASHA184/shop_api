from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session as _Session
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).resolve(strict=True).parent.parent))

from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, future=True, echo=False)
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False)

# Dependency
async def get_db():
    async with async_session() as session:
        yield session


Base = declarative_base()