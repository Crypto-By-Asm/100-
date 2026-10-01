from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from config.database import init_db
from api.market import router as market_router
from api.signals import router as signals_router
from api.blog import router as blog_router
from api.auth import router as auth_router
from api.demo import router as demo_router

BASE_DIR = Path(__file__).resolve().parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown

app = FastAPI(
    title=settings.app_name,
    description="AI-integrated crypto analytics, signals, demo trading and SEO blog platform by ASM Traders.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(market_router, prefix="/api/market", tags=["market"])
app.include_router(signals_router, prefix="/api/signals", tags=["signals"])
app.include_router(blog_router, prefix="/api/blog", tags=["blog"])
app.include_router(demo_router, prefix="/api/demo", tags=["demo"])

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return (BASE_DIR / "templates" / "index.html").read_text(encoding="utf-8")

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": "1.0.0",
    }
