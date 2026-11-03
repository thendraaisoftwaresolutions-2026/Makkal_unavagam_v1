from fastapi import FastAPI
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.database.connection import get_db
from app.api.v1.auth import router as auth_router

from app.api.v1.devices import router as devices_router
from app.api.v1.devices import router as devices_router
from app.api.v1.settings import router as settings_router
from app.api.v1.categories import router as categories_router
from app.api.v1.menu import router as menu_router
from app.api.v1.orders import router as orders_router

app = FastAPI(
    title="Makkal Unavagam API",
    description="Restaurant Management System API",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "Makkal Unavagam API is running",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "Makkal Unavagam"
    }

@app.get("/health/database")
def database_health(db: Session = Depends(get_db)):

    try:
        result = db.execute(
            text("SELECT current_database()")
        )

        database_name = result.scalar_one()

        return {
            "status": "connected",
            "database": database_name
        }

    except Exception as error:

        raise HTTPException(
            status_code=503,
            detail="Database connection unavailable"
        ) from error

app.include_router(
    auth_router,
    prefix="/api/v1",
)
app.include_router(devices_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(menu_router, prefix="/api/v1")

app.include_router(
    orders_router,
    prefix="/api/v1",
)