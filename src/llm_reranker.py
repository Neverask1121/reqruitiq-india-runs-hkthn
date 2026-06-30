from typing import List
from src.contracts import CandidateScore


# =========================
# SIMULATED LLM RE-RANKER
# (hackathon-safe version)
# =========================

def llm_score(candidate: CandidateScore) -> float:
    """
    Simulated LLM reasoning score (0–100)
    In real system → replace with OpenAI / local LLM
    """

    f = getattr(candidate, "debug_features", {})
    text = str(f.get("combined_text", "")).lower()

    score = 50  # base neutral

    # strong semantic boosts
    if "retrieval" in text or "ranking system" in text:
        score += 20

    if "vector" in text or "embedding" in text:
        score += 10

    if "spark" in text or "kafka" in text:
        score += 8

    if "ml" in text or "machine learning" in text:
        score += 7

    # penalty for weak relevance
    if "marketing manager" in text and "ai" not in text:
        score -= 10

    return max(0, min(100, score))


# =========================
# RE-RANK TOP-K ONLY
# =========================

def rerank_with_llm(candidates: List[CandidateScore], top_k: int = 20):

    top = candidates[:top_k]

    for c in top:
        c.llm_score = llm_score(c)

        # blend with existing score
        c.final_score = (0.7 * c.final_score) + (0.3 * c.llm_score)

    return sorted(candidates, key=lambda x: x.final_score, reverse=True)