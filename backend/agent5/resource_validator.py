"""
Agent 5 - Resource Validator Module
Checks that resource URLs are well-formed and from the approved free-only list.
"""

from __future__ import annotations
import re
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Approved free-resource domains
# ---------------------------------------------------------------------------
APPROVED_DOMAINS = {
    "w3schools.com",
    "www.w3schools.com",
    "geeksforgeeks.org",
    "freecodecamp.org",
    "kaggle.com",
    "khanacademy.org",
    "learn.microsoft.com",
    "microsoft.com",
    "developer.mozilla.org",
    "mdn.mozilla.org",
    "swayam.gov.in",
    "nptel.ac.in",
    "youtube.com",
    "youtu.be",
    "scikit-learn.org",
    "towardsdatascience.com",
    "medium.com",
    "github.com",
    "docs.python.org",
    "realpython.com",
    "tutorialspoint.com",
    "javatpoint.com",
    "coursera.org",
    "edx.org",
    "ocw.mit.edu",
    "archive.org",
    "sqlzoo.net",
    "learning.tcsionhub.in",
    "tcsionhub.in",
    "khanacademy.org",
    "fastapi.tiangolo.com",
    "tiangolo.com",
    "deeplearning.ai",
    "explore.skillbuilder.aws",
    "skillbuilder.aws",
    "aws.amazon.com",
    "docs.docker.com",
    "docker.com",
    "linuxjourney.com",
    "postgresqltutorial.com",
    "redis.io",
    "langchain-ai.github.io",
    "developers.google.com",
    "google.com",
}

_URL_REGEX = re.compile(
    r"^https?://"
    r"(?:(?:[A-Za-z0-9\-]+\.)+[A-Za-z]{2,})"
    r"(?:/[^\s]*)?$"
)


def is_valid_url(url):
    """Return True if the URL has a valid structure."""
    return bool(_URL_REGEX.match(url.strip()))


def is_approved_domain(url):
    """Return True if the URL's domain is in the approved free-resource list."""
    try:
        hostname = urlparse(url).hostname or ""
        hostname = hostname.lower()
        if hostname.startswith("www."):
            hostname = hostname[4:]
        for domain in APPROVED_DOMAINS:
            if hostname == domain or hostname.endswith("." + domain):
                return True
        return False
    except Exception:
        return False


def validate_schedule_links(schedule):
    """
    Validate all links in the schedule.
    Returns a list of warning dicts for any issues found.
    """
    warnings = []

    for entry in schedule:
        day = entry.get("day", "?")
        for field in ("priority_link", "optional_link"):
            url = entry.get(field, "")
            if not url:
                warnings.append({
                    "day": day,
                    "field": field,
                    "issue": "Empty URL",
                    "url": url,
                })
                continue
            if not is_valid_url(url):
                warnings.append({
                    "day": day,
                    "field": field,
                    "issue": "Malformed URL",
                    "url": url,
                })
            elif not is_approved_domain(url):
                warnings.append({
                    "day": day,
                    "field": field,
                    "issue": "Domain not in approved list",
                    "url": url,
                })

    return warnings


def print_validation_report(warnings):
    """Print a formatted validation report to the terminal."""
    if not warnings:
        print("  [OK] All resource links are valid and from approved free platforms.")
        return

    print("  [WARN] " + str(len(warnings)) + " validation warning(s) found:")
    for w in warnings:
        print("     Day " + str(w['day']) + " | " + w['field'] + ": " + w['issue'] + " -> " + w['url'])
