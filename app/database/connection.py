from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.config import config

if config.DEBUG:
    engine = create_async_engine(config.SQLALCHEMY_DATABASE_URI.unicode_string(), future=True, echo=True)
else:
    engine = create_async_engine(config.SQLALCHEMY_DATABASE_URI.unicode_string(), future=True, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

