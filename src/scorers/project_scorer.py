from src.contracts import Candidate, JobRequirements


class ProjectScorer:
    """
    Scores project relevance.
    Maximum = 15
    """

    MAX_SCORE = 15

    IMPORTANT_PROJECT_KEYWORDS = {
        "retrieval",
        "semantic search",
        "vector database",
        "recommendation",
        "ranking",
        "llm",
        "embeddings",
        "rag",
        "production ai",
    }

    def score(self, candidate: Candidate, job: JobRequirements,features):

        text = " ".join(candidate.projects).lower()

        matched = []

        for keyword in self.IMPORTANT_PROJECT_KEYWORDS:
            if keyword in text:
                matched.append(keyword)

        score = min(
            self.MAX_SCORE,
            len(matched) * 2
        )

        explanation = {
            "matched_projects": matched
        }

        return score, explanation