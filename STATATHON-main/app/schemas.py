from pydantic import BaseModel
from datetime import datetime
from typing import Dict

class DatasetOut(BaseModel):
    id: str
    filename: str
    path: str
    uploaded_at: datetime
    class Config:
        orm_mode = True

class SchemaMappingIn(BaseModel):
    dataset_id: str
    mapping: Dict[str, str]  # {raw_col: standard_col}

class SchemaMappingOut(BaseModel):
    id: str
    dataset_id: str
    mapping: Dict[str, str]
    created_at: datetime
    class Config:
        orm_mode = True
