from typing import List, Dict, Any
import numpy as np

def check_score_distribution_diversity(scores: List[float]) -> Dict[str, Any]:
    """
    Analyzes score distribution of the 100 benchmark candidates:
    - Min, Max, Mean, Median, Std Dev.
    - Distribution buckets (0-20, 21-40, 41-60, 61-80, 81-100).
    - Checks for variance and diversity.
    """
    if not scores:
        return {"diverse": False, "reason": "No scores available"}

    arr = np.array(scores)
    min_val = float(np.min(arr))
    max_val = float(np.max(arr))
    mean_val = float(np.mean(arr))
    median_val = float(np.median(arr))
    std_val = float(np.std(arr))

    # Bucket counts
    buckets = {
        "0-20": int(np.sum((arr >= 0) & (arr <= 20))),
        "21-40": int(np.sum((arr > 20) & (arr <= 40))),
        "41-60": int(np.sum((arr > 40) & (arr <= 60))),
        "61-80": int(np.sum((arr > 60) & (arr <= 80))),
        "81-100": int(np.sum((arr > 80) & (arr <= 100))),
    }

    # Meaningful diversity requires std_dev > 5.0 and span > 20 points
    is_diverse = (max_val - min_val >= 25.0) and (std_val >= 8.0)

    return {
        "diverse": is_diverse,
        "min_score": round(min_val, 2),
        "max_score": round(max_val, 2),
        "mean_score": round(mean_val, 2),
        "median_score": round(median_val, 2),
        "std_dev": round(std_val, 2),
        "distribution_buckets": buckets,
    }
