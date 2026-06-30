from typing import List

from src.contracts import Candidate, JobRequirements


class TechnicalScorer:
    """
    Scores candidates based on technical skill alignment.
    Maximum score returned = 35
    """

    MAX_SCORE = 35

    def score(self, candidate: Candidate, job: JobRequirements, features):

    skills = set([s.lower() for s in candidate.skills])

    score = 0
    matched_required = []

    if "python" in skills:
        score += 5
        matched_required.append("python")

    if features.get("llm_skill_count", 0) > 0:
        score += 3

    if features.get("retrieval_skill_count", 0) > 0:
        score += 5

    if features.get("vector_db_skill_count", 0) > 0:
        score += 5

    return score, {
        "matched_required": matched_required
    }