from fastapi import FastAPI
from app.routers import upload, schema_map, clean, analyze
from app import models
from app.db import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Survey Data Processor API",
    description="Backend for uploading and processing survey datasets",
    version="0.3.0"
)

app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(schema_map.router, prefix="/api", tags=["Schema Mapping"])
app.include_router(clean.router, prefix="/api", tags=["Cleaning"])
app.include_router(analyze.router, prefix="/api", tags=["Analysis"])

@app.get("/")
async def root():
    return {"message": "Survey Data Processor API is running!"}
