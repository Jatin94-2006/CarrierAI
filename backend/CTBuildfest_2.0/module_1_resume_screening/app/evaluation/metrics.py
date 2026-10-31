import math
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import scipy.stats as stats

def compute_classification_metrics(
    predicted_items: List[str],
    ground_truth_items: List[str]
) -> Dict[str, float]:
    """
    Computes Precision, Recall, and F1-score for sets of categorical or token items
    (e.g., extracted skills, exact entity names).
    """
    pred_set = {p.strip().lower() for p in predicted_items if p and p.strip()}
    gt_set = {g.strip().lower() for g in ground_truth_items if g and g.strip()}

    if not pred_set and not gt_set:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "exact_match": 1.0}
    if not pred_set or not gt_set:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "exact_match": 0.0}

    true_positives = len(pred_set.intersection(gt_set))
    precision = true_positives / len(pred_set) if pred_set else 0.0
    recall = true_positives / len(gt_set) if gt_set else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    exact_match = 1.0 if pred_set == gt_set else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "exact_match": exact_match
    }

def compute_evidence_correctness(
    evidence_snippets: List[str],
    source_document_text: str
) -> Dict[str, Any]:
    """
    Verifies evidence snippets extracted by LLM actually exist in raw source text
    to prevent LLM hallucination and ensure auditability.
    """
    if not evidence_snippets:
        return {"total_snippets": 0, "verified_snippets": 0, "veracity_ratio": 1.0, "hallucinated_count": 0}

    source_lower = source_document_text.lower()
    verified = 0
    hallucinated = 0

    for snippet in evidence_snippets:
        snippet_clean = " ".join(snippet.lower().split())
        # Check if snippet or substantial substring is in source
        if snippet_clean in source_lower or any(part in source_lower for part in snippet_clean.split(". ") if len(part) > 15):
            verified += 1
        else:
            hallucinated += 1

    ratio = verified / len(evidence_snippets) if evidence_snippets else 1.0
    return {
        "total_snippets": len(evidence_snippets),
        "verified_snippets": verified,
        "hallucinated_count": hallucinated,
        "veracity_ratio": round(ratio, 4)
    }

def compute_score_agreement(
    system_scores: List[float],
    human_scores: List[float]
) -> Dict[str, float]:
    """
    Calculates agreement metrics between deterministic system ATS scores and human benchmark reviewer scores.
    Computes Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and Pearson r.
    """
    if not system_scores or not human_scores or len(system_scores) != len(human_scores):
        raise ValueError("System scores and human scores must be non-empty and of identical length.")

    sys_arr = np.array(system_scores, dtype=float)
    hum_arr = np.array(human_scores, dtype=float)

    mae = float(np.mean(np.abs(sys_arr - hum_arr)))
    mse = float(np.mean((sys_arr - hum_arr) ** 2))
    rmse = math.sqrt(mse)

    # Pearson correlation if variance > 0
    if np.std(sys_arr) > 1e-6 and np.std(hum_arr) > 1e-6:
        pearson_r, _ = stats.pearsonr(sys_arr, hum_arr)
        pearson_r = float(pearson_r)
    else:
        pearson_r = 1.0 if np.allclose(sys_arr, hum_arr) else 0.0

    return {
        "mae": round(mae, 4),
        "mse": round(mse, 4),
        "rmse": round(rmse, 4),
        "pearson_r": round(pearson_r, 4)
    }

def compute_ranking_correlation(
    system_ranks: List[int],
    human_ranks: List[int]
) -> Dict[str, float]:
    """
    Computes Spearman rank correlation rho and Kendall's tau between system ranking and human reviewer rankings.
    """
    if not system_ranks or not human_ranks or len(system_ranks) != len(human_ranks):
        raise ValueError("System ranks and human ranks must be non-empty and of identical length.")

    if len(system_ranks) < 2:
        return {"spearman_rho": 1.0, "kendall_tau": 1.0}

    spearman_rho, _ = stats.spearmanr(system_ranks, human_ranks)
    kendall_tau, _ = stats.kendalltau(system_ranks, human_ranks)

    return {
        "spearman_rho": round(float(spearman_rho) if not np.isnan(spearman_rho) else 1.0, 4),
        "kendall_tau": round(float(kendall_tau) if not np.isnan(kendall_tau) else 1.0, 4)
    }

def compute_ndcg_at_k(
    relevance_scores_ranked_by_system: List[float],
    k: int = 5
) -> float:
    """
    Computes Normalized Discounted Cumulative Gain (NDCG@k) for ranking evaluation.
    relevance_scores_ranked_by_system: True human relevance scores ordered by the system's rank.
    """
    if not relevance_scores_ranked_by_system:
        return 0.0

    k = min(k, len(relevance_scores_ranked_by_system))
    actual_k = relevance_scores_ranked_by_system[:k]

    # DCG calculation
    dcg = sum((2 ** rel - 1) / math.log2(idx + 2) for idx, rel in enumerate(actual_k))

    # Ideal DCG calculation (sorted descending)
    ideal_k = sorted(relevance_scores_ranked_by_system, reverse=True)[:k]
    idcg = sum((2 ** rel - 1) / math.log2(idx + 2) for idx, rel in enumerate(ideal_k))

    if idcg == 0:
        return 1.0 if dcg == 0 else 0.0

    return round(float(dcg / idcg), 4)

def compute_confidence_calibration(
    confidences: List[float],
    accuracies: List[int],
    num_bins: int = 5
) -> Dict[str, float]:
    """
    Computes Expected Calibration Error (ECE) to verify that AI confidence scores
    faithfully match actual empirical accuracy.
    """
    if not confidences or not accuracies or len(confidences) != len(accuracies):
        return {"expected_calibration_error": 0.0}

    bin_boundaries = np.linspace(0, 1, num_bins + 1)
    ece = 0.0
    total_samples = len(confidences)

    for i in range(num_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]

        # Samples within bin
        in_bin = [
            (c, a) for c, a in zip(confidences, accuracies)
            if (bin_lower <= c < bin_upper) or (i == num_bins - 1 and bin_lower <= c <= bin_upper)
        ]

        if in_bin:
            bin_conf = sum(c for c, _ in in_bin) / len(in_bin)
            bin_acc = sum(a for _, a in in_bin) / len(in_bin)
            ece += (len(in_bin) / total_samples) * abs(bin_acc - bin_conf)

    return {"expected_calibration_error": round(float(ece), 4)}
