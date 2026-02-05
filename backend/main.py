from dotenv import load_dotenv
from pathlib import Path
# Load env variables
load_dotenv(dotenv_path=Path(__file__).resolve().with_name(".env"))

import models
from database import engine
from sqlalchemy import inspect, text
from app_factory import create_app
from security import ensure_secret_key

# Ensure required secrets are set (skips in TEST_MODE)
ensure_secret_key()

# Create Tables
models.Base.metadata.create_all(bind=engine)


def ensure_quiz_result_time_columns(db_engine):
    inspector = inspect(db_engine)
    if "quiz_results" not in inspector.get_table_names():
        return

    existing = {col["name"] for col in inspector.get_columns("quiz_results")}
    with db_engine.begin() as connection:
        if "duration_seconds" not in existing:
            connection.execute(text("ALTER TABLE quiz_results ADD COLUMN duration_seconds INTEGER DEFAULT 0"))
        if "active_seconds" not in existing:
            connection.execute(text("ALTER TABLE quiz_results ADD COLUMN active_seconds INTEGER DEFAULT 0"))


ensure_quiz_result_time_columns(engine)

app = create_app()
