from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from api.routers import game, session
from core.auth import is_request_authorized
from core.logging import get_logger, log_event
from core.rate_limiter import InMemoryRateLimiter

# Khởi tạo biến "app" mà Uvicorn đang tìm kiếm:
app = FastAPI(
    title="NeuroCorp Heist API",
    description="Multi-Model AI Red Teaming & Prompt Injection Backend",
    version="1.0.0",
)

logger = get_logger("neurocorp.backend")
rate_limiter = InMemoryRateLimiter(requests=60, window_seconds=60)

# Cấu hình CORS để React Frontend (localhost:5173) có thể kết nối:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add basic security headers and rate-limit public requests."""

    if not is_request_authorized(request):
        log_event(logger, event="unauthorized_request", path=request.url.path)
        return Response(status_code=401, content="Unauthorized", media_type="text/plain")

    client_key = request.client.host if request.client else "unknown"
    if not rate_limiter.allow(client_key):
        log_event(logger, event="rate_limited", client=client_key, path=request.url.path)
        return Response(status_code=429, content="Too Many Requests", media_type="text/plain")

    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


app.include_router(session.router)
app.include_router(game.router)

# Endpoint kiểm tra sức khỏe hệ thống:
@app.get("/health", tags=["System Diagnostics"])
async def health_check():
    return {
        "status": "ONLINE",
        "system": "NeuroCorp Security Gateway",
        "message": "Backend engine is primed and ready for prompt injection."
    }