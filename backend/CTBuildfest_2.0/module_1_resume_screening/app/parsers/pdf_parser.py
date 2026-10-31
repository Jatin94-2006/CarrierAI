import io
from typing import Tuple
import pymupdf
from app.core.logging import logger
from app.utils.text_cleaner import clean_and_normalize_text, is_text_insufficient_or_scanned

def extract_text_from_pdf(pdf_bytes: bytes) -> Tuple[str, bool]:
    """
    Extracts text from PDF bytes using PyMuPDF.
    If the document appears to be scanned or contains insufficient text,
    it flags scanned=True for OCR fallback.
    Returns (cleaned_text, is_scanned).
    """
    raw_text = []
    is_scanned = False
    
    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text:
                raw_text.append(text)
        doc.close()
    except Exception as e:
        logger.error(f"PyMuPDF failed to parse PDF: {e}")
        return "", True

    full_text = "\n".join(raw_text)
    cleaned = clean_and_normalize_text(full_text)
    
    if is_text_insufficient_or_scanned(cleaned):
        logger.info("PDF has insufficient digital text. Flagged as scanned/image-based.")
        is_scanned = True
        
    return cleaned, is_scanned
