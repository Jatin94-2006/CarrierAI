import json
import re
from typing import Any, Dict, Optional

def extract_json_from_llm_response(response_text: str) -> Dict[str, Any]:
    """
    Extracts valid JSON dictionary from LLM output, handling markdown blocks and whitespace.
    """
    if not response_text:
        return {}
        
    text = response_text.strip()
    
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
    # Check for markdown code fences: ```json ... ``` or ``` ... ```
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text, re.IGNORECASE)
    if match:
        extracted = match.group(1).strip()
        try:
            return json.loads(extracted)
        except json.JSONDecodeError:
            pass
            
    # Try finding first { and last }
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end+1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
            
    # Try finding first [ and last ]
    start = text.find('[')
    end = text.rfind(']')
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end+1]
        try:
            return {"items": json.loads(candidate)}
        except json.JSONDecodeError:
            pass

    return {}
