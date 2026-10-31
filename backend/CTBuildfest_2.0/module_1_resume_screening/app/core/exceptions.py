from fastapi import HTTPException, status

class BaseScreeningException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class FileValidationError(BaseScreeningException):
    def __init__(self, detail: str = "Invalid file uploaded"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class FileExtractionError(BaseScreeningException):
    def __init__(self, detail: str = "Failed to extract content from file"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

class AIProcessingError(BaseScreeningException):
    def __init__(self, detail: str = "AI model processing failed"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)

class SessionNotFoundError(BaseScreeningException):
    def __init__(self, detail: str = "Screening session not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class ResourceNotFoundError(BaseScreeningException):
    def __init__(self, detail: str = "Requested resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
