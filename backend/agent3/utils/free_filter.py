"""
Agent 3: Course Suggestion Agent
Free resource verification — allowlist/denylist approach.
"""

from urllib.parse import urlparse

# ─── Known FREE platforms ─────────────────────────────────────────────────────
FREE_DOMAINS = {
    # Technical learning
    "w3schools.com",
    "geeksforgeeks.org",
    "freecodecamp.org",
    "kaggle.com",
    "learn.microsoft.com",
    "microsoft.com",
    "developer.mozilla.org",
    "mdn.dev",
    "swayam.gov.in",
    "nptel.ac.in",
    "youtube.com",
    "youtu.be",
    "khanacademy.org",
    "tutorialspoint.com",
    "javatpoint.com",
    "programiz.com",
    "codecademy.com",      # has free tier
    "cs50.harvard.edu",
    "edx.org",             # free audit
    "ocw.mit.edu",
    "developers.google.com",
    "cloud.google.com",
    "aws.amazon.com",      # free training catalog
    "trailhead.salesforce.com",
    "analyticsvidhya.com",
    "towardsdatascience.com",
    "realpython.com",
    "python.org",
    "docs.python.org",
    "sqlzoo.net",
    "sqlbolt.com",
    "mode.com",
    "learnsql.com",
    "pgexercises.com",
    "datacamp.com",        # has free intro courses
    "github.com",
    "roadmap.sh",

    # Soft skills / Indian platforms
    "tcsion.com",
    "nsdc.gov.in",
    "pmkvyofficial.org",
    "nsdcindia.org",
    "skillindiadigital.gov.in",
    "diksha.gov.in",

    # General open education
    "coursera.org",        # audit / financial aid
    "futurelearn.com",
    "openlearning.com",
    "saylor.org",
    "alison.com",
}

# ─── Known PAID-ONLY platforms (block these) ──────────────────────────────────
PAID_DOMAINS = {
    "udemy.com",
    "pluralsight.com",
    "linkedin.com/learning",
    "skillshare.com",
    "masterclass.com",
    "treehouse.com",
    "brilliant.org",
}

# ─── Keywords that suggest a resource is NOT free ────────────────────────────
PAID_KEYWORDS = [
    "buy now",
    "purchase",
    "subscribe to access",
    "premium only",
    "pro plan",
    "pricing",
    "$",
    "enroll for",
    "pay ",
]


def get_domain(url: str) -> str:
    """Extract the base domain from a URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        return domain
    except Exception:
        return ""


def is_likely_free(url: str, title: str = "", description: str = "") -> bool:
    """
    Returns True if the resource is likely free.

    Strategy:
    1. If domain is in PAID_DOMAINS → False
    2. If domain is in FREE_DOMAINS → True
    3. Check title/description for paid keywords → False
    4. Unknown domain → True (optimistic, filter again after fetch if needed)
    """
    domain = get_domain(url)

    # Hard block paid domains
    for paid in PAID_DOMAINS:
        if paid in domain:
            return False

    # Trust known free domains
    for free in FREE_DOMAINS:
        if free in domain:
            return True

    # Keyword heuristics on title + description
    combined = (title + " " + description).lower()
    for kw in PAID_KEYWORDS:
        if kw in combined:
            return False

    # Unknown domain — optimistically include but mark for review
    return True


def filter_free_resources(resources: list) -> list:
    """Filter a list of resource dicts/objects to only free ones."""
    filtered = []
    for r in resources:
        if isinstance(r, dict):
            url = r.get("url", "")
            title = r.get("title", "")
            desc = r.get("description", "")
        else:
            url = getattr(r, "url", "")
            title = getattr(r, "title", "")
            desc = getattr(r, "description", "")

        if is_likely_free(url, title, desc):
            filtered.append(r)

    return filtered


def deduplicate_by_url(resources: list) -> list:
    """Remove duplicate resources by URL."""
    seen_urls = set()
    unique = []
    for r in resources:
        url = r.get("url", "") if isinstance(r, dict) else getattr(r, "url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(r)
    return unique


# ─── Platform name from domain ────────────────────────────────────────────────
DOMAIN_TO_PLATFORM = {
    "w3schools.com": "W3Schools",
    "geeksforgeeks.org": "GeeksforGeeks",
    "freecodecamp.org": "freeCodeCamp",
    "kaggle.com": "Kaggle Learn",
    "learn.microsoft.com": "Microsoft Learn",
    "developer.mozilla.org": "MDN Web Docs",
    "swayam.gov.in": "SWAYAM",
    "nptel.ac.in": "NPTEL",
    "youtube.com": "YouTube",
    "youtu.be": "YouTube",
    "khanacademy.org": "Khan Academy",
    "tutorialspoint.com": "TutorialsPoint",
    "programiz.com": "Programiz",
    "cs50.harvard.edu": "Harvard CS50",
    "realpython.com": "Real Python",
    "sqlzoo.net": "SQLZoo",
    "sqlbolt.com": "SQLBolt",
    "analyticsvidhya.com": "Analytics Vidhya",
    "tcsion.com": "TCS iON",
    "skillindiadigital.gov.in": "Skill India Digital",
    "diksha.gov.in": "DIKSHA",
    "coursera.org": "Coursera (Audit Free)",
    "edx.org": "edX (Audit Free)",
    "github.com": "GitHub",
    "roadmap.sh": "Roadmap.sh",
}


def platform_from_url(url: str) -> str:
    domain = get_domain(url)
    for key, name in DOMAIN_TO_PLATFORM.items():
        if key in domain:
            return name
    return domain.replace("www.", "").split(".")[0].capitalize()
