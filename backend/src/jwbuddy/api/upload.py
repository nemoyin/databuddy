from __future__ import annotations
import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, HTTPException
from jwbuddy.config import settings

router = APIRouter(prefix="/upload", tags=["upload"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".txt", ".csv", ".json", ".md", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

UPLOAD_DIR = Path(settings.data_dir) / "uploads"


@router.post("")
async def upload_file(file: UploadFile):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过 10MB 限制")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Sanitize: strip any directory components to prevent path traversal
    import time
    safe_basename = os.path.basename(file.filename or "upload")
    safe_name = f"{int(time.time())}_{safe_basename}"
    file_path = UPLOAD_DIR / safe_name
    file_path.write_bytes(content)

    return {
        "filename": file.filename,
        "file_path": safe_name,
        "size": len(content),
        "content_type": file.content_type,
    }
