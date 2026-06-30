from src.contracts import Candidate, JobRequirements
from src.scorer import CandidateScorer


def main():
    candidate = Candidate(
        candidate_id="C001",
        skills=[
            "Python",
            "Embeddings",
            "Vector Databases",
            "LangChain",
            "LLM",
        ],
        experience_years=4,
    )

    job = JobRequirements(
        mandatory_skills=[
            "Python",
            "Embeddings",
            "Retrieval Systems",
            "Ranking Systems",
            "Vector Databases",
        ],
        preferred_skills=[
            "LoRA",
            "Open Source",
        ],
    )

    scorer = CandidateScorer()

    result = scorer.score(candidate, job)

    print(result)


if __name__ == "__main__":
    main()