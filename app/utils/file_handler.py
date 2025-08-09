import os
from app.config import UPLOAD_DIR

def save_upload_file(upload_file) -> str:
    """
    Saves uploaded file to UPLOAD_DIR and returns the file path.
    """
    file_path = os.path.join(UPLOAD_DIR, upload_file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(upload_file.file.read())
    return file_path
