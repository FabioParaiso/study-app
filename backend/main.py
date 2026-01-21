from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import models
from database import engine
from routers import auth, study, gamification

# Load env variables
load_dotenv()

# Create Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(study.router)
app.include_router(gamification.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
