from fastapi import FastAPI

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