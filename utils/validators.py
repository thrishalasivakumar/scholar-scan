from pathlib import Path
from typing import Optional

MAX_PDF_SIZE_MB = 50


def validate_uploaded_pdf(file_name: str, file_size: int) -> Optional[str]:
    suffix = Path(file_name).suffix.lower()

    if suffix != ".pdf":
        return "Please upload a valid PDF file."

    max_bytes = MAX_PDF_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        return f"File is too large. Please upload a PDF under {MAX_PDF_SIZE_MB} MB."

    return None


def validate_query(query: str) -> Optional[str]:
    if not query or not query.strip():
        return "Summary focus cannot be empty."

    if len(query.strip()) < 12:
        return "Please provide a more specific focus query (at least 12 characters)."

    return None
