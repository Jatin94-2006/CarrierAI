import re
from datetime import datetime, date
from typing import List, Tuple, Optional

MONTH_MAP = {
    'jan': 1, 'january': 1,
    'feb': 2, 'february': 2,
    'mar': 3, 'march': 3,
    'apr': 4, 'april': 4,
    'may': 5,
    'jun': 6, 'june': 6,
    'jul': 7, 'july': 7,
    'aug': 8, 'august': 8,
    'sep': 9, 'september': 9, 'sept': 9,
    'oct': 10, 'october': 10,
    'nov': 11, 'november': 11,
    'dec': 12, 'december': 12
}

def parse_date_string(date_str: Optional[str]) -> Optional[date]:
    """
    Parses various date formats from resumes:
    - 'January 2022', 'Jan 2022', '01/2022', '2022'
    - 'Present', 'Current', 'Till date'
    """
    if not date_str:
        return None
    
    clean = date_str.strip().lower()
    if clean in ["present", "current", "now", "till date", "ongoing"]:
        return date.today()
    
    # Try Month Year (e.g. Jan 2021 or January 2021)
    m = re.search(r'([a-z]+)[\s,.-]+(\d{4})', clean)
    if m:
        month_name, year = m.group(1), int(m.group(2))
        month = MONTH_MAP.get(month_name, 1)
        return date(year, month, 1)
        
    # Try MM/YYYY or MM-YYYY
    m = re.search(r'(\d{1,2})[/-](\d{4})', clean)
    if m:
        month, year = int(m.group(1)), int(m.group(2))
        month = max(1, min(12, month))
        return date(year, month, 1)
        
    # Try Year only (e.g. 2021)
    m = re.search(r'\b(19\d{2}|20\d{2})\b', clean)
    if m:
        year = int(m.group(1))
        return date(year, 1, 1)
        
    return None

def merge_overlapping_intervals(intervals: List[Tuple[date, date]]) -> List[Tuple[date, date]]:
    """
    Merges overlapping date intervals to prevent double-counting experience.
    """
    if not intervals:
        return []
    
    # Filter valid intervals where start <= end
    valid = [i for i in intervals if i[0] and i[1] and i[0] <= i[1]]
    if not valid:
        return []
        
    sorted_intervals = sorted(valid, key=lambda x: x[0])
    merged = [sorted_intervals[0]]
    
    for current in sorted_intervals[1:]:
        prev_start, prev_end = merged[-1]
        curr_start, curr_end = current
        
        if curr_start <= prev_end:
            # Overlapping or adjacent, merge
            merged[-1] = (prev_start, max(prev_end, curr_end))
        else:
            merged.append(current)
            
    return merged

def calculate_total_experience_years(date_pairs: List[Tuple[Optional[str], Optional[str]]]) -> Tuple[float, bool]:
    """
    Calculates total non-overlapping experience in years.
    Returns (years, has_unverified_dates).
    """
    parsed_intervals: List[Tuple[date, date]] = []
    has_unverified = False
    
    for start_str, end_str in date_pairs:
        start_d = parse_date_string(start_str)
        end_d = parse_date_string(end_str) or (date.today() if start_d else None)
        
        if start_d and end_d:
            if start_d <= end_d:
                parsed_intervals.append((start_d, end_d))
            else:
                has_unverified = True
        else:
            if start_str or end_str:
                has_unverified = True
                
    merged = merge_overlapping_intervals(parsed_intervals)
    
    total_days = 0
    for s, e in merged:
        total_days += (e - s).days + 30 # include month
        
    years = round(total_days / 365.25, 2)
    return max(0.0, years), has_unverified
