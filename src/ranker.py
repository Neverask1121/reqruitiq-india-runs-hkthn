from typing import List

from src.data_loader import load_candidates
from src.preprocessing import preprocess_all
from src.scorer import score_all
from src.weighted_ranker import rank_candidates
from src.reasoning import generate_reasoning
from src.llm_reranker import rerank_with_llm
from src.evaluation import evaluate_ranking


# =========================
# PIPELINE CONTROLLER
# =========================

def run_pipeline(input_path: str, top_k: int = 100):

    print("\n[1] Loading candidates...")
    raw_candidates = load_candidates(input_path)

    print("[2] Preprocessing...")
    preprocessed = preprocess_all(raw_candidates)

    print("[3] Scoring candidates...")
    scored = score_all(preprocessed)

    print("[4] Ranking candidates (weighted + JD boost)...")
    ranked = rank_candidates(scored)
    ranked = rerank_with_llm(ranked, top_k=20)

    print("[5] Selecting Top-K...")
    top_candidates = ranked[:top_k]
    evaluate_ranking(ranked)

    print(f"[DONE] Final selected: {len(top_candidates)} candidates")

    return top_candidates


# =========================
# CSV EXPORT READY DATA
# =========================

def prepare_submission_rows(top_candidates: List):

    rows = []

    for rank, c in enumerate(top_candidates, start=1):

        rows.append({
            "candidate_id": c.candidate_id,
            "rank": rank,
            "final_score": round(c.final_score, 2),
            "reasoning": getattr(c, "reasoning", "No reasoning available")
        })

    return rows


# =========================
# MAIN ENTRY
# =========================

from src.utils import save_submission


if __name__ == "__main__":

    input_path = "dataset/sample_candidates.json"

    top_candidates = run_pipeline(input_path)

    rows = prepare_submission_rows(top_candidates)

    save_submission(rows)