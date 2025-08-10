from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import SessionLocal
from app.models import Dataset, SchemaMapping
from app.schemas import SchemaMappingIn, SchemaMappingOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/schema-map", response_model=SchemaMappingOut)
async def create_schema_mapping(payload: SchemaMappingIn, db: Session = Depends(get_db)):
    # Check dataset exists
    dataset = db.query(Dataset).filter(Dataset.id == payload.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    schema_map = SchemaMapping(dataset_id=payload.dataset_id, mapping=payload.mapping)
    db.add(schema_map)
    db.commit()
    db.refresh(schema_map)
    return schema_map


@router.get("/schema-map/{dataset_id}", response_model=List[SchemaMappingOut])
async def get_schema_mappings(dataset_id: str, db: Session = Depends(get_db)):
    mappings = db.query(SchemaMapping).filter(SchemaMapping.dataset_id == dataset_id).all()
    if not mappings:
        raise HTTPException(status_code=404, detail="No mappings found for this dataset")
    return mappings
