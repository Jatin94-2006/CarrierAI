import os
import sys

# Ensure module_1_resume_screening is in sys.path
_module_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _module_root not in sys.path:
    sys.path.insert(0, _module_root)

from app.evaluation.metrics import (
    compute_classification_metrics,
    compute_evidence_correctness,
    compute_score_agreement,
    compute_ranking_correlation,
    compute_ndcg_at_k,
    compute_confidence_calibration
)
from app.evaluation.runner import EvaluationFramework

__all__ = [
    "compute_classification_metrics",
    "compute_evidence_correctness",
    "compute_score_agreement",
    "compute_ranking_correlation",
    "compute_ndcg_at_k",
    "compute_confidence_calibration",
    "EvaluationFramework"
]
