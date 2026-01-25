from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os


def configure_rate_limiter(app: FastAPI) -> None:
    if Path(__file__).parent.name != "tests" and not Path.cwd().name == "tests":
        if os.getenv("TEST_MODE") != "true":
            from slowapi import Limiter, _rate_limit_exceeded_handler
            from slowapi.errors import RateLimitExceeded
            from slowapi.util import get_remote_address

            limiter = Limiter(key_func=get_remote_address)
            app.state.limiter = limiter
            app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
            return
    app.state.limiter = None


def configure_middlewares(app: FastAPI) -> None:
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def register_routes(app: FastAPI) -> None:
    from routers import auth, gamification
    from modules.materials import router as materials_router
    from modules.quizzes import router as quizzes_router
    from modules.analytics import router as analytics_router

    app.include_router(auth.router)
    app.include_router(materials_router.router)
    app.include_router(quizzes_router.router)
    app.include_router(analytics_router.router)
    app.include_router(gamification.router)

    @app.get("/health")
    def health_check():
        return {"status": "ok"}


def create_app() -> FastAPI:
    app = FastAPI()
    configure_rate_limiter(app)
    configure_middlewares(app)
    register_routes(app)
    return app
