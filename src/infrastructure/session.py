from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
