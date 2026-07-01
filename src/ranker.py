from pathlib import Path
import subprocess
import sys
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_candidates
from src.preprocessing import preprocess_all
from src.scorer import score_all
from src.weighted_ranker import rank_candidates
from src.llm_reranker import rerank_with_llm
from src.evaluation import evaluate_ranking


PARSED_CANDIDATES_PATH = PROJECT_ROOT / "member2" / "outputs" / "parsed_candidates.json"
RANKED_OUTPUT_PATH = PROJECT_ROOT / "public" / "ranked_candidates.json"


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

    ordered_candidates = sorted(
        top_candidates,
        key=lambda c: (-round(float(c.final_score or 0.0), 2), c.candidate_id)
    )

    for rank, c in enumerate(ordered_candidates, start=1):

        rows.append({
            "candidate_id": c.candidate_id,
            "rank": rank,
            "score": round(c.final_score, 2),
            "reasoning": getattr(c, "reasoning", "No reasoning available")
        })

    return rows


def ensure_parsed_candidates() -> str:
    parsed_path = PARSED_CANDIDATES_PATH
    if parsed_path.exists():
        return str(parsed_path)

    print("[1b] Parsed candidates not found; running Member 2 dataset processor...")
    subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "member2" / "scripts" / "process_dataset.py")],
        check=True
    )
    return str(parsed_path)


# =========================
# MAIN ENTRY
# =========================

from src.utils import save_submission


if __name__ == "__main__":
    input_path = ensure_parsed_candidates()
    top_candidates = run_pipeline(input_path)

    rows = prepare_submission_rows(top_candidates)

    save_submission(rows)
    from src.utils import save_ranked_candidates
    save_ranked_candidates(
        rows,
        str(RANKED_OUTPUT_PATH),
        metadata={
            "generated_at": "backend-run",
            "top_k": len(rows),
            "total_candidates": len(rows),
        },
    )
