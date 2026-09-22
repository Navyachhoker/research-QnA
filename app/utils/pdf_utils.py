"""Extract text per page from a PDF."""

from pathlib import Path

import fitz  # PyMuPDF


class PDFExtractionError(ValueError):
    """Raised when a PDF can't be opened or has no extractable text."""


def extract_text_by_page(pdf_path: str | Path) -> list[dict]:
    """
    Extract text from every page of a PDF.

    Returns a list of {"page_number": int, "text": str}, skipping blank
    pages (e.g. pure-image scans with no text layer).

    Raises PDFExtractionError for corrupt, encrypted, or unreadable files
    instead of letting a low-level PyMuPDF exception propagate as a 500.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise PDFExtractionError(f"PDF not found: {pdf_path}")

    try:
        document = fitz.open(pdf_path)
    except Exception as exc:  # PyMuPDF raises its own exception types
        raise PDFExtractionError(f"Could not open PDF: {exc}") from exc

    try:
        if document.is_encrypted:
            raise PDFExtractionError("PDF is password-protected and cannot be processed.")

        pages = []
        for page_number in range(len(document)):
            text = document[page_number].get_text("text").strip()
            if text:
                pages.append({"page_number": page_number + 1, "text": text})
    finally:
        document.close()

    if not pages:
        raise PDFExtractionError(
            "No extractable text found in this PDF. It may be a scanned "
            "image with no text layer (OCR is not currently supported)."
        )

    return pages
