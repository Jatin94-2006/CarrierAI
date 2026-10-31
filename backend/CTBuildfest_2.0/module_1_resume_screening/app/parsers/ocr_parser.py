import io
from app.core.logging import logger
from app.utils.text_cleaner import clean_and_normalize_text

def apply_ocr_fallback(file_bytes: bytes) -> str:
    """
    Applies OCR extraction on scanned or image-based document bytes.
    Uses pytesseract if installed, or pymupdf pixmap rendering with fallback.
    """
    try:
        import pytesseract
        from PIL import Image
        import pymupdf

        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        ocr_texts = []
        for i in range(len(doc)):
            page = doc[i]
            pix = page.get_pixmap(dpi=150)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img)
            if text:
                ocr_texts.append(text)
        doc.close()
        return clean_and_normalize_text("\n".join(ocr_texts))
    except Exception as e:
        logger.warning(f"OCR fallback could not process image (Tesseract not configured or error): {e}")
        return ""
