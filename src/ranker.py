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

        projects=[
            "Built a Retrieval System using Vector Database",
            "Implemented Semantic Search with Embeddings",
        ],

        behavioral_signals={
            "open_to_work": True,
            "github_activity": 120,
            "recruiter_response_rate": 85,
        },
        education=["B.Tech Computer Science",],
        certifications=[""
            "AWS Cloud Practitioner",
            "TensorFlow Developer",
],
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