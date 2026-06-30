from src.contracts import Candidate, JobRequirements


class ExperienceScorer:
    """
    Scores candidate experience.
    Maximum = 25
    """

    MAX_SCORE = 25

    def score(self, candidate: Candidate, job: JobRequirements):
        years = candidate.experience_years

        if years >= 5:
            score = 25
        elif years >= 3:
            score = 20
        elif years >= 2:
            score = 15
        elif years >= 1:
            score = 10
        else:
            score = 5

        explanation = {
            "experience_years": years
        }

        return score, explanation