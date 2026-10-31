import json
from typing import Dict, Any, Union
from app.schemas.resume import ResumeStructuredData
from app.core.exceptions import FileValidationError

def parse_resume_json(json_input: Union[str, bytes, Dict[str, Any]]) -> ResumeStructuredData:
    """
    Parses and validates a candidate resume supplied as structured JSON.
    """
    if isinstance(json_input, (str, bytes)):
        try:
            data = json.loads(json_input)
        except Exception as e:
            raise FileValidationError(f"Invalid JSON format: {e}")
    else:
        data = json_input

    try:
        validated = ResumeStructuredData(**data)
        # Ensure flat skills list is populated
        if not validated.all_skills_flat:
            flat = []
            for field in [
                validated.skills.programming_languages,
                validated.skills.frameworks,
                validated.skills.libraries,
                validated.skills.databases,
                validated.skills.cloud_technologies,
                validated.skills.tools,
                validated.skills.soft_skills,
                validated.skills.domain_specific_skills,
            ]:
                flat.extend(field)
            validated.all_skills_flat = list(dict.fromkeys(flat))
        return validated
    except Exception as e:
        raise FileValidationError(f"JSON does not adhere to Resume schema: {e}")
