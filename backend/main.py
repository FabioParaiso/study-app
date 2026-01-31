from dotenv import load_dotenv
# Load env variables
load_dotenv()

import models
from database import engine
from app_factory import create_app
from security import ensure_secret_key

# Ensure required secrets are set (skips in TEST_MODE)
ensure_secret_key()

# Create Tables
models.Base.metadata.create_all(bind=engine)

app = create_app()
