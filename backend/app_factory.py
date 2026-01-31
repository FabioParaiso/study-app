from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os


def configure_rate_limiter(app: FastAPI) -> None:
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from rate_limiter import limiter

    if os.getenv("TEST_MODE") == "true":
        limiter.enabled = False

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def configure_middlewares(app: FastAPI) -> None:
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    raw_origins = os.getenv("ALLOWED_ORIGINS", "")
    if raw_origins:
        allow_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    else:
        allow_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

    allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "false").strip().lower() in {"1", "true", "yes", "on"}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )


def register_routes(app: FastAPI) -> None:
    from modules.auth import router as auth_router
    from modules.gamification import router as gamification_router
    from modules.materials import router as materials_router
    from modules.quizzes import router as quizzes_router
    from modules.analytics import router as analytics_router

    app.include_router(auth_router.router)
    app.include_router(materials_router.router)
    app.include_router(quizzes_router.router)
    app.include_router(analytics_router.router)
    app.include_router(gamification_router.router)

    @app.get("/health")
    def health_check():
        return {"status": "ok"}


def create_app() -> FastAPI:
    app = FastAPI()
    configure_rate_limiter(app)
    configure_middlewares(app)
    register_routes(app)
    return app
