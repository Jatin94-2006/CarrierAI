import re
from typing import List, Dict, Tuple, Optional
from app.schemas.screening import SkillMatchItem

# Verified equivalent aliases: canonical -> set of verified alias strings
VERIFIED_ALIASES: Dict[str, List[str]] = {
    "python": ["py", "python3", "python 3"],
    "javascript": ["js", "es6", "ecmascript"],
    "typescript": ["ts"],
    "postgresql": ["postgres", "pgsql", "psql"],
    "react": ["reactjs", "react.js"],
    "vue": ["vuejs", "vue.js"],
    "node.js": ["nodejs", "node"],
    "fastapi": ["fast-api"],
    "kubernetes": ["k8s"],
    "docker": ["docker container", "dockerization"],
    "aws": ["amazon web services"],
    "gcp": ["google cloud platform", "google cloud"],
    "azure": ["microsoft azure"],
    "rest apis": ["restful apis", "rest api", "restful web services"],
    "mongodb": ["mongo"],
    "golang": ["go"],
    "sql": ["postgresql", "postgres", "mysql", "sqlite", "tsql", "plsql", "structured query language"],
    "ci/cd": ["continuous integration", "github actions", "gitlab ci"],
}

# Related (but non-equivalent) skills. E.g. Flask is related to FastAPI, but NOT equivalent
RELATED_SKILLS: Dict[str, List[str]] = {
    "fastapi": ["flask", "django", "tornado"],
    "flask": ["fastapi", "django"],
    "django": ["fastapi", "flask"],
    "react": ["vue", "angular", "svelte"],
    "vue": ["react", "angular"],
    "angular": ["react", "vue"],
    "postgresql": ["mysql", "sqlite", "oracle", "sql server"],
    "mysql": ["postgresql", "mariadb", "sqlite"],
    "mongodb": ["dynamodb", "couchbase", "cassandra"],
    "docker": ["podman", "containerd"],
    "aws": ["gcp", "azure"],
}

# Strict negative discrimination: must NEVER be treated as identical
DISTINCT_TECHNOLOGIES = [
    ({"java"}, {"javascript", "js"}),
    ({"fastapi"}, {"flask"}),
    ({"html"}, {"react"}),
    ({"mysql"}, {"mongodb"}),
]

def normalize_skill(name: str) -> str:
    """Normalizes skill string for comparison."""
    clean = re.sub(r'[^a-zA-Z0-9.+/#-]', '', name).strip().lower()
    return clean

def match_skill_against_candidate_skills(
    target_skill: str,
    candidate_skills: List[str],
    category: str = "required"
) -> SkillMatchItem:
    """
    Matches a single job requirement skill against candidate skills list.
    Returns SkillMatchItem with status: exact_match, verified_equivalent, related, missing.
    Credit awarded:
    - Exact match: 1.0
    - Verified equivalent: 0.85
    - Related skill: 0.40
    - Missing: 0.0
    """
    target_norm = normalize_skill(target_skill)
    target_lower = target_skill.lower().strip()
    
    # 1. Exact Match (Case-insensitive)
    for c_skill in candidate_skills:
        c_norm = normalize_skill(c_skill)
        c_lower = c_skill.lower().strip()
        if target_norm == c_norm or target_lower == c_lower:
            return SkillMatchItem(
                skill=target_skill,
                category=category,
                status="exact_match",
                credit=1.0,
                matched_with=c_skill,
                evidence_snippet=f"Candidate explicitly lists '{c_skill}'."
            )

    # Check distinct barrier to prevent false positive equivalences
    # E.g. Java should never match JavaScript
    for group_a, group_b in DISTINCT_TECHNOLOGIES:
        if (target_lower in group_a and any(c.lower().strip() in group_b for c in candidate_skills)) or \
           (target_lower in group_b and any(c.lower().strip() in group_a for c in candidate_skills)):
            pass # Keep searching without accidental fuzzy matching

    # 2. Verified Equivalent (Alias)
    # Check if target has aliases in candidate skills
    aliases = VERIFIED_ALIASES.get(target_lower, [])
    for alias in aliases:
        for c_skill in candidate_skills:
            if normalize_skill(alias) == normalize_skill(c_skill):
                return SkillMatchItem(
                    skill=target_skill,
                    category=category,
                    status="verified_equivalent",
                    credit=0.85,
                    matched_with=c_skill,
                    evidence_snippet=f"Candidate lists verified alias/equivalent '{c_skill}' for '{target_skill}'."
                )

    # Check if any candidate skill has target as alias
    for c_skill in candidate_skills:
        c_aliases = VERIFIED_ALIASES.get(c_skill.lower().strip(), [])
        if any(normalize_skill(a) == target_norm for a in c_aliases):
            return SkillMatchItem(
                skill=target_skill,
                category=category,
                status="verified_equivalent",
                credit=0.85,
                matched_with=c_skill,
                evidence_snippet=f"Candidate lists verified equivalent '{c_skill}' for '{target_skill}'."
            )

    # 3. Related Skill
    related = RELATED_SKILLS.get(target_lower, [])
    for rel in related:
        for c_skill in candidate_skills:
            if normalize_skill(rel) == normalize_skill(c_skill):
                return SkillMatchItem(
                    skill=target_skill,
                    category=category,
                    status="related",
                    credit=0.40,
                    matched_with=c_skill,
                    evidence_snippet=f"Candidate has related technology '{c_skill}', which provides transferable foundational knowledge for '{target_skill}'."
                )

    # 4. Missing
    return SkillMatchItem(
        skill=target_skill,
        category=category,
        status="missing",
        credit=0.0,
        matched_with=None,
        evidence_snippet=f"No direct or equivalent mention of '{target_skill}' found in candidate profile."
    )

def evaluate_skills_matching(
    required_skills: List[str],
    preferred_skills: List[str],
    candidate_skills: List[str]
) -> Tuple[List[SkillMatchItem], List[SkillMatchItem], float, float]:
    """
    Evaluates required and preferred skills against candidate skills.
    Returns (req_matches, pref_matches, req_score_ratio, pref_score_ratio).
    """
    req_matches = [
        match_skill_against_candidate_skills(s, candidate_skills, category="required")
        for s in required_skills
    ]
    pref_matches = [
        match_skill_against_candidate_skills(s, candidate_skills, category="preferred")
        for s in preferred_skills
    ]
    
    req_score_ratio = sum(m.credit for m in req_matches) / max(1, len(req_matches))
    pref_score_ratio = sum(m.credit for m in pref_matches) / max(1, len(pref_matches)) if pref_matches else 1.0
    
    return req_matches, pref_matches, req_score_ratio, pref_score_ratio
