from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Dataset
from app.utils.analyzer import (
    compute_weighted_stats,
    plot_to_base64,
    correlation_heatmap,
    boxplot_column,
    pie_chart,
    scatter_plot, generate_chart_caption
)
from app.utils.report_generator import generate_report
import pandas as pd
import os

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/analyze/{dataset_id}")
async def analyze_dataset(dataset_id: str, weight_col: str = Query(None), db: Session = Depends(get_db)):
    # 1️⃣ Fetch dataset
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # 2️⃣ Locate cleaned dataset
    cleaned_path = dataset.path.replace(dataset.filename, f"cleaned_{dataset.filename}")
    if not os.path.exists(cleaned_path):
        raise HTTPException(status_code=400, detail="Cleaned dataset not found. Run cleaning first.")

    # 3️⃣ Load cleaned data
    df = pd.read_csv(cleaned_path)

    # Drop columns that are fully NaN
    df = df.dropna(axis=1, how='all')

    # 4️⃣ Compute statistics
    stats = compute_weighted_stats(df, weight_col=weight_col)

    charts = []
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()

    # 5️⃣ Distributions (first 3 non-empty columns)
    for col in df.columns[:3]:
        charts.append({"col": f"Distribution: {col}", "img": plot_to_base64(col, df), "caption": generate_chart_caption(df, col)})

    # 6️⃣ Correlation heatmap
    corr_img = correlation_heatmap(df)
    if corr_img:
        charts.append({"col": "Correlation Heatmap", "img": corr_img})

    # 7️⃣ Boxplots (first 2 numeric columns)
    for col in numeric_cols[:2]:
        charts.append({"col": f"Boxplot: {col}", "img": boxplot_column(df, col), "caption": generate_chart_caption(df, col)})

    # 8️⃣ Pie chart (first categorical column with <= 10 unique values)
    if cat_cols and df[cat_cols[0]].nunique() <= 30:
        charts.append({"col": f"Pie Chart: {cat_cols[0]}", "img": pie_chart(df, cat_cols[0]), "caption": generate_chart_caption(df, cat_cols[0])})

    # 9️⃣ Scatter plot (first 2 numeric columns)
    if len(numeric_cols) >= 2:
        charts.append({
            "col": f"Scatter Plot: {numeric_cols[0]} vs {numeric_cols[1]}",
            "img": scatter_plot(df, numeric_cols[0], numeric_cols[1])
        })

    # 🔟 Generate PDF report
    pdf_path = cleaned_path.replace("cleaned_", "report_").replace(".csv", ".pdf")
    generate_report(stats, charts, pdf_path)

    return {
        "message": "Analysis completed with extended visuals",
        "pdf_report_path": pdf_path,
        "stats": stats
    }
