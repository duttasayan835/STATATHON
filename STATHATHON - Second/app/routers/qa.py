from fastapi import APIRouter, Query
from app.utils.qa_gemini import ask_gemini_question
import os
import PyPDF2

router = APIRouter()

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, "rb") as f:  # Read binary
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        raise Exception(f"Failed to read PDF: {str(e)}")
    return text.strip()

@router.post("/qa")
async def qa_session(
    question: str = Query(...),
    report_path: str = Query(...)
):
    if not os.path.exists(report_path):
        return {"error": "Report file not found."}

    try:
        report_content = extract_text_from_pdf(report_path)
    except Exception as e:
        return {"error": str(e)}

    if not report_content.strip():
        return {"error": "Report has no readable text."}

    answer = ask_gemini_question(question, report_content)
    return {"question": question, "answer": answer}
