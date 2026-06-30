class FeatureEngineer:
    """
    Creates derived features for scoring.
    """

    def extract_features(self, candidate, job):
        return {
            "skill_count": len(candidate.skills),
            "project_count": len(candidate.projects),
            "experience": candidate.experience_years,
        }