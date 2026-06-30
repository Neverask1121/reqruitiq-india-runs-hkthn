from src.scorers.technical_scorer import TechnicalScorer
from src.contracts import Candidate,JobRequirements,CandidateScore
from src.scorers.experience_scorer import ExperienceScorer

class CandidateScorer:
    """
    Main orchestrator for all scoring modules.
    Combines all individual scorers into one final candidate score.
    """
    def __init__(self):
        self.technical=TechnicalScorer()
        self.experience=ExperienceScorer()

    def score(self,candidate:Candidate,job:JobRequirements)->CandidateScore:
        tech_score, tech_exp = self.technical.score(candidate, job)
        exp_score,exp_exp=self.experience.score(candidate,job)

        final=CandidateScore(
            candidate_id=candidate.candidate_id,
            technical_score=tech_score,
            experience_score=exp_score,
            project_score=0,
            behavioral_score=0,
            culture_score=0,
            education_score=0,
            
            final_score=tech_score+exp_score,
            strengths=[],
            weaknesses=[],

        )

        final.strengths.extend(tech_exp["matched_required"])

        return final