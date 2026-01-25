from dotenv import load_dotenv
import models
from database import engine
from app_factory import create_app

# Load env variables
load_dotenv()

# Create Tables
models.Base.metadata.create_all(bind=engine)

app = create_app()
