from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import models
from database import engine
from routers import auth, study, gamification

# ...

# Include Routers
app.include_router(auth.router)
app.include_router(study.router)
app.include_router(gamification.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
