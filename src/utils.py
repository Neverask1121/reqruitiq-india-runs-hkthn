from pathlib import Path
import csv
import json


REQUIRED_COLUMNS = ["candidate_id", "rank", "score", "reasoning"]


def save_submission(rows, output_path="outputs/submission.csv"):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "candidate_id": row["candidate_id"],
                "rank": row["rank"],
                "score": row["score"],
                "reasoning": row["reasoning"],
            })

    print(f"[SAVED] Submission written to {output_path}")


def save_ranked_candidates(rows, output_path="public/ranked_candidates.json", metadata=None):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        payload = {
            "candidates": rows,
        }
        if metadata:
            payload.update(metadata)
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    print(f"[SAVED] Ranked candidates written to {output_path}")
