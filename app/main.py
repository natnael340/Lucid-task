# app/main.py

from fastapi import FastAPI
from .routes import router
from .models import Base
from .config import engine

app = FastAPI()

# Create database tables (for development, consider using migrations in production)
Base.metadata.create_all(bind=engine)

app.include_router(router)
