from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.file_handler import save_upload_file
from app.models import Dataset
from app.db import SessionLocal
import pandas as pd
from typing import List
from app.schemas import DatasetOut

router = APIRouter()


# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".csv", ".xlsx")):
        raise HTTPException(status_code=400, detail="Only CSV or Excel files are allowed")

    file_path = save_upload_file(file)

    # Try reading first 5 rows for preview
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file_path, nrows=5)
        else:
            df = pd.read_excel(file_path, nrows=5)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    # Save dataset info in DB
    dataset = Dataset(filename=file.filename, path=file_path)
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    return {
        "message": "File uploaded successfully",
        "dataset_id": dataset.id,
        "filename": file.filename,
        "preview": df.to_dict(orient="records")
    }


@router.get("/datasets", response_model=List[DatasetOut])
async def list_datasets(db: Session = Depends(get_db)):
    datasets = db.query(Dataset).all()
    return datasets
