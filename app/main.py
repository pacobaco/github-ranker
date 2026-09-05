from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app.routers import auth, billing, ranking, orgs, health

Base.metadata.create_all(bind=engine)
app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_url,"http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(billing.router)
app.include_router(ranking.router)
app.include_router(orgs.router)
