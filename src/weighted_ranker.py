from typing import List

from src.contracts import CandidateScore


# =========================
# FINAL RANKING BOOST LOGIC
# =========================

def jd_relevance_boost(score: CandidateScore) -> float:
    """
    Boost candidates who are ACTUALLY relevant to JD:
    ranking / retrieval / ML infra
    """

    boost = 0.0
    f = getattr(score, "debug_features", {})

    text = str(f.get("combined_text", "")).lower()

    # CORE JD MATCH SIGNALS
    if "retrieval" in text:
        boost += 8

    if "ranking" in text or "recommendation system" in text:
        boost += 10

    if "vector" in text or "embedding" in text:
        boost += 6

    if "spark" in text and "kafka" in text:
        boost += 5

    # STRONG REAL ENGINEERING SIGNAL
    if f.get("data_eng_score", 0) > 50:
        boost += 5

    return boost


# =========================
# NOISE PENALTY
# =========================

def noise_penalty(score: CandidateScore) -> float:
    f = getattr(score, "debug_features", {})
    text = str(f.get("combined_text", "")).lower()

    penalty = 0.0

    # weak engagement penalty
    if f.get("activity_score", 0) < 10:
        penalty += 5

    # fake AI signal penalty
    if "chatgpt" in text and "engineering" not in text:
        penalty += 3

    # irrelevant marketing profiles
    if "marketing manager" in text and "ai" in text:
        penalty += 4

    return penalty


# =========================
# FINAL SCORE ADJUSTMENT
# =========================

def adjust_final_score(score: CandidateScore) -> float:
    base = float(score.final_score or 0)

    boost = jd_relevance_boost(score)
    penalty = noise_penalty(score)

    return max(0.0, base + boost - penalty)


# =========================
# MAIN RANKER
# =========================

def rank_candidates(scores: List[CandidateScore]) -> List[CandidateScore]:

    for s in scores:
        s.final_score = adjust_final_score(s)

    # SORT FINAL LIST
    ranked = sorted(
        scores,
        key=lambda x: (-float(x.final_score or 0.0), x.candidate_id)
    )

    return ranked
