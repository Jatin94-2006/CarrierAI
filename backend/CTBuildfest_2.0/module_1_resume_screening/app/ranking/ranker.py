from typing import List, Tuple
from app.schemas.screening import CandidateRankingResult, ScoreDistributionStats
from app.schemas.persona import SyntheticPersonaItem
from app.personas.diversity_checker import check_score_distribution_diversity

def compute_candidate_ranking(
    actual_score: float,
    synthetic_pool: List[SyntheticPersonaItem]
) -> Tuple[CandidateRankingResult, ScoreDistributionStats]:
    """
    Ranks the actual candidate among 101 total profiles (1 real + 100 synthetic).
    Applies the exact formula from Section 10:
    Percentile = (Number of synthetic candidates scoring below actual candidate / 100) * 100
    """
    synthetic_scores = [p.ats_score for p in synthetic_pool]
    total_synthetic = len(synthetic_scores)  # 100
    
    above_count = sum(1 for s in synthetic_scores if s > actual_score)
    below_count = sum(1 for s in synthetic_scores if s < actual_score)
    tied_count = sum(1 for s in synthetic_scores if s == actual_score)

    # Rank is 1-indexed. If 23 are higher, rank is 24
    rank = above_count + 1
    total_compared = total_synthetic + 1  # 101 candidates

    # Formula: (synthetic_below / 100) * 100
    percentile = round((below_count / max(1, total_synthetic)) * 100.0, 2)

    explanation = (
        f"Your ATS score of {actual_score} places you at the {percentile}th percentile among a 100-candidate synthetic benchmark. "
        f"{below_count} candidates scored lower, {above_count} scored higher, and {tied_count} tied. "
        "Notice: This is a synthetic talent pool benchmark, not a real-world applicant roster or hiring guarantee."
    )

    ranking_res = CandidateRankingResult(
        actual_candidate_score=actual_score,
        total_candidates_compared=total_compared,
        rank=rank,
        synthetic_candidates_above=above_count,
        synthetic_candidates_below=below_count,
        synthetic_candidates_tied=tied_count,
        percentile=percentile,
        comparison_type="synthetic_benchmark",
        explanation=explanation
    )

    # Score distribution stats
    all_scores = synthetic_scores + [actual_score]
    diversity_info = check_score_distribution_diversity(all_scores)

    # Competency band counts
    band_counts = {}
    for p in synthetic_pool:
        band_counts[p.competency_band] = band_counts.get(p.competency_band, 0) + 1

    distribution_stats = ScoreDistributionStats(
        min_score=diversity_info["min_score"],
        max_score=diversity_info["max_score"],
        mean_score=diversity_info["mean_score"],
        median_score=diversity_info["median_score"],
        std_dev=diversity_info["std_dev"],
        distribution_buckets=diversity_info["distribution_buckets"],
        band_counts=band_counts
    )

    return ranking_res, distribution_stats
