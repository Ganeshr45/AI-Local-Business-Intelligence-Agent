from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.db import models
from app.api import runs, ask
from app.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Local Business Intelligence Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(runs.router, prefix="/api")
app.include_router(ask.router, prefix="/api")


@app.get("/")
def health_check():
    return {"status": "ok", "mock_mode": settings.mock_mode}
