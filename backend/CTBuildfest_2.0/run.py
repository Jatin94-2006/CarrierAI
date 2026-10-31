import os
import sys
import uvicorn

# Add module_1_resume_screening to python path
current_dir = os.path.dirname(os.path.abspath(__file__))
module_dir = os.path.join(current_dir, "module_1_resume_screening")
if module_dir not in sys.path:
    sys.path.insert(0, module_dir)

from app.config import settings

if __name__ == "__main__":
    print(f"Starting {settings.APP_NAME} on http://{settings.HOST}:{settings.PORT}")
    print(f"Interactive Swagger Documentation available at http://127.0.0.1:{settings.PORT}/docs")
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True, reload_dirs=[module_dir])
