import math
from typing import List


# =========================
# DCG
# =========================

def dcg(scores: List[float]) -> float:
    return sum([
        (2 ** rel - 1) / math.log2(i + 2)
        for i, rel in enumerate(scores)
    ])


# =========================
# NDCG
# =========================

def ndcg(predicted: List[float], ideal: List[float]) -> float:

    if not predicted or not ideal:
        return 0.0

    ideal_dcg = dcg(sorted(ideal, reverse=True))
    pred_dcg = dcg(predicted)

    if ideal_dcg == 0:
        return 0.0

    return pred_dcg / ideal_dcg


# =========================
# SIMPLE EVAL WRAPPER
# =========================

def evaluate_ranking(candidates):

    # simulate relevance using final_score bucketed
    predicted = [c.final_score for c in candidates]

    # ideal ranking = sorted best possible
    ideal = sorted(predicted, reverse=True)

    score = ndcg(predicted, ideal)

    print(f"[NDCG SCORE]: {round(score, 4)}")

    return score