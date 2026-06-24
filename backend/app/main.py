import socketio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.database import Base, engine
from app.models import Meeting, MeetingParticipant, User, ChatMessage, BookingProfile, BookingAvailability  # noqa: F401
from app.routes import auth, meetings, scheduler
from app.websocket.signaling import sio

Base.metadata.create_all(bind=engine)

from sqlalchemy import text
from app.utils.rate_limit import limiter

# Safely add new columns to existing tables
try:
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_pic VARCHAR;"))
except Exception as e:
    print(f"Error updating schema: {e}")

fastapi_app = FastAPI(
    title=f"{settings.app_name} - Developed by Nishant Panwar", 
    version="1.0.0",
    description="Backend Project created and secured by Nishant Panwar"
)
fastapi_app.state.limiter = limiter
fastapi_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@fastapi_app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Developer"] = "Nishant Panwar"
    response.headers["X-Project-Owner"] = "Nishant Panwar"
    return response

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
fastapi_app.include_router(auth.router)
fastapi_app.include_router(meetings.router)
fastapi_app.include_router(scheduler.router)


@fastapi_app.get("/api/health", tags=["System"])
def health():
    return {
        "status": "ok", 
        "service": settings.app_name, 
        "developer": "Nishant Panwar",
        "security": "Encrypted & Secured by Nishant Panwar"
    }


app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app, socketio_path="socket.io")
