import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine

from alembic import context
from app.storage import Base

load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)
config = context.config
target_metadata = Base.metadata
url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
if config.attributes.get("connection") is not None:
    context.configure(connection=config.attributes["connection"], target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
elif context.is_offline_mode():
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    with create_engine(url).connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
