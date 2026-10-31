import pytest
from app.evaluation.metrics import (
    compute_classification_metrics,
    compute_evidence_correctness,
    compute_score_agreement,
    compute_ranking_correlation,
    compute_ndcg_at_k,
    compute_confidence_calibration
)
from app.evaluation.runner import EvaluationFramework

def test_classification_metrics():
    preds = ["python", "fastapi", "docker"]
    gt = ["python", "fastapi", "kubernetes"]
    metrics = compute_classification_metrics(preds, gt)
    
    assert metrics["precision"] == round(2 / 3, 4)
    assert metrics["recall"] == round(2 / 3, 4)
    assert metrics["f1"] == round(2 / 3, 4)
    assert metrics["exact_match"] == 0.0

def test_classification_exact_match():
    preds = ["python", "sql"]
    gt = ["sql", "python"]
    metrics = compute_classification_metrics(preds, gt)
    assert metrics["exact_match"] == 1.0
    assert metrics["f1"] == 1.0

def test_evidence_correctness():
    source = "Senior Python engineer with 5 years experience in building high-throughput FastAPI systems."
    evidence = [
        "Senior Python engineer",
        "FastAPI systems",
        "Expert in blockchain smart contracts"  # Not present
    ]
    ev_metrics = compute_evidence_correctness(evidence, source)
    assert ev_metrics["total_snippets"] == 3
    assert ev_metrics["verified_snippets"] == 2
    assert ev_metrics["hallucinated_count"] == 1
    assert ev_metrics["veracity_ratio"] == round(2 / 3, 4)

def test_score_agreement():
    sys_scores = [80.0, 70.0, 60.0]
    human_scores = [82.0, 68.0, 61.0]
    agreement = compute_score_agreement(sys_scores, human_scores)
    assert agreement["mae"] == pytest.approx(1.6667, rel=1e-3)
    assert agreement["pearson_r"] > 0.9

def test_ranking_correlation_and_ndcg():
    sys_ranks = [1, 2, 3, 4, 5]
    hum_ranks = [1, 2, 4, 3, 5]
    corr = compute_ranking_correlation(sys_ranks, hum_ranks)
    assert corr["spearman_rho"] > 0.8
    assert corr["kendall_tau"] > 0.7

    # NDCG
    relevances = [1.0, 0.8, 0.6, 0.4, 0.2]
    ndcg = compute_ndcg_at_k(relevances, k=5)
    assert ndcg == 1.0

def test_confidence_calibration():
    confs = [0.9, 0.8, 0.7, 0.6]
    accs = [1, 1, 1, 0]
    calib = compute_confidence_calibration(confs, accs)
    assert "expected_calibration_error" in calib
    assert calib["expected_calibration_error"] >= 0.0

def test_evaluation_framework_runner():
    framework = EvaluationFramework(dataset_version="v1.0-test")
    report = framework.run_benchmark()
    
    assert "evaluation_metadata" in report
    assert report["evaluation_metadata"]["dataset_version"] == "v1.0-test"
    assert "metrics" in report
    assert "skill_matching" in report["metrics"]
    assert "score_agreement" in report["metrics"]
    assert "ranking_correlation" in report["metrics"]
    assert "ndcg_at_5" in report["metrics"]["ranking_correlation"]
