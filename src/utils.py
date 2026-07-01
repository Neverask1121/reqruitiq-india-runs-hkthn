import pandas as pd


def save_submission(rows, output_path="outputs/submission.csv"):

    df = pd.DataFrame(rows)

    # enforce column order EXACTLY
    df = df[["candidate_id", "rank", "final_score", "reasoning"]]

    df.to_csv(output_path, index=False)

    print(f"[SAVED] Submission written to {output_path}")