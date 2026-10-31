import pytest
from app.ranking.ranker import compute_candidate_ranking
from app.schemas.persona import SyntheticPersonaItem
from app.schemas.resume import ResumeStructuredData

def test_ranking_and_percentile_formula():
    # Construct 100 synthetic personas with scores from 1.0 to 100.0
    synthetic_pool = []
    for i in range(1, 101):
        item = SyntheticPersonaItem(
            id=f"syn_{i}",
            competency_band="middle",
            profile=ResumeStructuredData(),
            ats_score=float(i)
        )
        synthetic_pool.append(item)

    # Actual candidate with score 78.5
    actual_score = 78.5
    ranking, distribution = compute_candidate_ranking(actual_score, synthetic_pool)

    # Synthetic candidates below 78.5: scores 1 to 78 -> exactly 78 candidates
    # Synthetic candidates above 78.5: scores 79 to 100 -> exactly 22 candidates
    assert ranking.synthetic_candidates_below == 78
    assert ranking.synthetic_candidates_above == 22
    assert ranking.synthetic_candidates_tied == 0
    assert ranking.rank == 23 # 22 above + 1
    assert ranking.total_candidates_compared == 101
    
    # Formula: (synthetic_below / 100) * 100 -> 78.0
    assert ranking.percentile == 78.0

def test_tie_handling():
    synthetic_pool = []
    # 50 at score 50, 50 at score 80
    for i in range(50):
        synthetic_pool.append(SyntheticPersonaItem(
            id=f"syn_low_{i}", competency_band="low", profile=ResumeStructuredData(), ats_score=50.0
        ))
    for i in range(50):
        synthetic_pool.append(SyntheticPersonaItem(
            id=f"syn_high_{i}", competency_band="high", profile=ResumeStructuredData(), ats_score=80.0
        ))

    actual_score = 50.0
    ranking, _ = compute_candidate_ranking(actual_score, synthetic_pool)
    assert ranking.synthetic_candidates_tied == 50
    assert ranking.synthetic_candidates_above == 50
    assert ranking.synthetic_candidates_below == 0
    assert ranking.percentile == 0.0
    assert ranking.rank == 51
