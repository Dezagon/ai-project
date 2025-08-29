from fastapi import Depends, FastAPI

from app.database import get_db
from app.routers import ai, auth, notes

app = FastAPI(title="AI Study Helper")

app.include_router(ai.router)
app.include_router(auth.router)
app.include_router(notes.router)