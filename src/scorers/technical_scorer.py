from typing import List

from src.contracts import Candidate, JobRequirements


class TechnicalScorer:
    """
    Scores candidates based on technical skill alignment.
    Maximum score returned = 35
    """

    MAX_SCORE = 35

    def score(self, candidate: Candidate, job: JobRequirements):
        candidate_skills = {
            skill.lower().strip()
            for skill in candidate.skills
        }

        required_skills = {
            skill.lower().strip()
            for skill in job.mandatory_skills
        }

        preferred_skills = {
            skill.lower().strip()
            for skill in job.preferred_skills
        }

        matched_required = candidate_skills & required_skills
        matched_preferred = candidate_skills & preferred_skills

        if len(required_skills) == 0:
            required_score = 0
        else:
            required_score = (
                len(matched_required)
                / len(required_skills)
            ) * 30

        if len(preferred_skills) == 0:
            preferred_score = 0
        else:
            preferred_score = (
                len(matched_preferred)
                / len(preferred_skills)
            ) * 5

        final_score = min(
            self.MAX_SCORE,
            required_score + preferred_score,
        )

        explanation = {
            "matched_required": sorted(matched_required),
            "matched_preferred": sorted(matched_preferred),
            "missing_required": sorted(
                required_skills - matched_required
            ),
        }

        return final_score, explanation