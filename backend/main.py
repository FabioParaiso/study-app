from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from pathlib import Path
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import models
from database import engine
from routers import auth, study, gamification

# Load env variables
load_dotenv()

# Create Tables
models.Base.metadata.create_all(bind=engine)

# Rate Limiter (disabled in test mode)
app = FastAPI()

if Path(__file__).parent.name != "tests" and not Path.cwd().name == "tests":
    # Only enable rate limiting in production/dev, not in tests
    import os
    if os.getenv("TEST_MODE") != "true":
        limiter = Limiter(key_func=get_remote_address)
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    else:
        # Test mode: create a dummy limiter that does nothing
        app.state.limiter = None
else:
    app.state.limiter = None

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# CORS Configuration
# Sentinel [HIGH]: Restrict allowed origins to prevent unauthorized cross-origin access.
# Allow standard dev ports and production overrides via env var.
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

env_origins = os.getenv("ALLOWED_ORIGINS")
if env_origins:
    origins.extend([origin.strip() for origin in env_origins.split(",")])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
