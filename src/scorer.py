from src.contracts import Candidate, JobRequirements, CandidateScore

from src.scorers.technical_scorer import TechnicalScorer
from src.scorers.experience_scorer import ExperienceScorer
from src.scorers.project_scorer import ProjectScorer
from src.scorers.behavioral_scorer import BehavioralScorer
from src.scorers.education_scorer import EducationScorer
from src.scorers.culture_scorer import CultureScorer
class CandidateScorer:
    """
    Main orchestrator for all scoring modules.
    """

    def __init__(self):
        self.technical = TechnicalScorer()
        self.experience = ExperienceScorer()
        self.project = ProjectScorer()
        self.behavior = BehavioralScorer()
        self.education = EducationScorer()
        self.culture = CultureScorer()

    def score(
        self,
        candidate: Candidate,
        job: JobRequirements,
    ) -> CandidateScore:

        tech_score, tech_exp = self.technical.score(candidate, job)
        exp_score, exp_exp = self.experience.score(candidate, job)
        project_score, project_exp = self.project.score(candidate, job)
        behavior_score, behavior_exp = self.behavior.score(candidate, job)
        education_score, education_exp = self.education.score(candidate,job,)
        culture_score, culture_exp = self.culture.score(candidate, job)


        final = CandidateScore(
            candidate_id=candidate.candidate_id,

            technical_score=tech_score,
            experience_score=exp_score,
            project_score=project_score,
            behavioral_score=behavior_score,

            education_score=education_score,
            culture_score=culture_score,

            final_score=(
                tech_score
                + exp_score
                + project_score
                + behavior_score+ education_score+ culture_score
            ),
            
            strengths=[],
            weaknesses=[],
        )

        final.strengths.extend(
            tech_exp["matched_required"]
        )

        return final