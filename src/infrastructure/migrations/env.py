from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from src.config import settings
from src.infrastructure.models import Base

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_online():
    url = (
        f"postgresql+psycopg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.POSTGRES_DB}"
    )
    engine = create_engine(url)

    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
