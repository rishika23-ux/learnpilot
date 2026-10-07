from fastapi import HTTPException, UploadFile

ALLOWED_CONTENT_TYPES = {"application/pdf"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


async def validate_upload(file: UploadFile) -> bytes:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File too large (max 20MB)")

    if not contents.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="File is not a valid PDF")

    return contents