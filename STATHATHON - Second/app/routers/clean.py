from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Dataset, SchemaMapping
from app.utils.data_cleaner import apply_mapping, validate_and_clean
import pandas as pd

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/clean/{dataset_id}")
async def clean_dataset(
        dataset_id: str,
        config: dict = Body(...),  # cleaning configuration
        db: Session = Depends(get_db)
):
    # Get dataset
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Get latest mapping for this dataset
    mapping_obj = db.query(SchemaMapping).filter(SchemaMapping.dataset_id == dataset_id).order_by(
        SchemaMapping.created_at.desc()).first()
    if not mapping_obj:
        raise HTTPException(status_code=400, detail="No schema mapping found for this dataset")

    # Load file
    try:
        if dataset.filename.endswith(".csv"):
            df = pd.read_csv(dataset.path)
        else:
            df = pd.read_excel(dataset.path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

    # Apply mapping & clean
    df = apply_mapping(df, mapping_obj.mapping)
    df_clean, report = validate_and_clean(df, config)

    # Save cleaned file
    cleaned_path = dataset.path.replace(dataset.filename, f"cleaned_{dataset.filename}")
    df_clean.to_csv(cleaned_path, index=False)

    return {
        "message": "Dataset cleaned successfully",
        "cleaned_file_path": cleaned_path,
        "report": report
    }
