import io
from docx import Document
from app.core.logging import logger
from app.utils.text_cleaner import clean_and_normalize_text

def extract_text_from_docx(docx_bytes: bytes) -> str:
    """
    Extracts text from DOCX bytes including paragraphs and table contents.
    """
    try:
        file_stream = io.BytesIO(docx_bytes)
        doc = Document(file_stream)
        text_parts = []
        
        # Extract normal paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text.strip())
                
        # Extract tables
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    text_parts.append(" | ".join(row_text))
                    
        full_text = "\n".join(text_parts)
        return clean_and_normalize_text(full_text)
    except Exception as e:
        logger.error(f"Failed to extract DOCX text: {e}")
        return ""
