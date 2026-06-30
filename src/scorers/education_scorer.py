from src.contracts import Candidate, JobRequirements


class EducationScorer:
    """
    Scores education and certifications.
    Maximum score = 5
    """

    MAX_SCORE = 5

    def score(
        self,
        candidate: Candidate,
        job: JobRequirements,
    ):
        score = 0
        explanation = {
            "education": [],
            "certifications": [],
        }

        education_text = " ".join(candidate.education).lower()

        if any(
            degree in education_text
            for degree in [
                "computer science",
                "software engineering",
                "information technology",
                "artificial intelligence",
                "machine learning",
            ]
        ):
            score += 3
            explanation["education"].append(
                "Relevant technical education"
            )

        if len(candidate.certifications) > 0:
            score += 2
            explanation["certifications"] = candidate.certifications

        score = min(score, self.MAX_SCORE)

        return score, explanation