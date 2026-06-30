class ReasonGenerator:
    """
    Generates explanations for candidate scores.
    """

    def generate(self, candidate_score):
        return {
            "final_score": candidate_score.final_score,
            "strengths": candidate_score.strengths,
            "weaknesses": candidate_score.weaknesses,
        }