from src.contracts import Candidate, JobRequirements


class BehavioralScorer:
    """
    Scores behavioral signals.
    Maximum = 15
    """

    MAX_SCORE = 15

    def score(self, candidate: Candidate, job: JobRequirements):
        score = 0

        signals = candidate.behavioral_signals

        if signals.get("open_to_work", False):
            score += 5

        if signals.get("github_activity", 0) > 50:
            score += 5

        if signals.get("recruiter_response_rate", 0) > 70:
            score += 5

        explanation = {
            "behavioral_signals": signals
        }

        return min(score, self.MAX_SCORE), explanation