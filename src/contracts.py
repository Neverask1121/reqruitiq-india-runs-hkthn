from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


# =========================
# PROFILE STRUCTURES
# =========================

@dataclass
class Skill:
    name: str
    proficiency: str
    endorsements: int = 0
    duration_months: int = 0


@dataclass
class Education:
    institution: str
    degree: str
    field_of_study: str
    start_year: int
    end_year: int
    grade: str = ""
    tier: str = ""


@dataclass
class Job:
    company: str
    title: str
    start_date: str
    end_date: Optional[str]
    duration_months: int
    is_current: bool
    industry: str = ""
    company_size: str = ""
    description: str = ""


@dataclass
class Profile:
    anonymized_name: str
    headline: str
    summary: str
    location: str
    country: str
    years_of_experience: float
    current_title: str
    current_company: str
    current_company_size: str
    current_industry: str


# =========================
# SIGNALS
# =========================

@dataclass
class RedrobSignals:
    profile_completeness_score: float
    signup_date: str
    last_active_date: str
    open_to_work_flag: bool

    profile_views_received_30d: int
    applications_submitted_30d: int
    recruiter_response_rate: float
    avg_response_time_hours: float

    connection_count: int
    endorsements_received: int
    notice_period_days: int

    expected_salary_range_inr_lpa: Dict[str, float]

    preferred_work_mode: str
    willing_to_relocate: bool

    github_activity_score: float

    search_appearance_30d: int
    saved_by_recruiters_30d: int

    interview_completion_rate: float
    offer_acceptance_rate: float

    verified_email: bool
    verified_phone: bool
    linkedin_connected: bool


# =========================
# CANDIDATE ENTITY
# =========================

@dataclass
class Candidate:
    candidate_id: str
    profile: Profile

    career_history: List[Job] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    skills: List[Skill] = field(default_factory=list)

    certifications: List[Any] = field(default_factory=list)
    languages: List[Any] = field(default_factory=list)

    redrob_signals: Optional[RedrobSignals] = None


# =========================
# SCORING CONTRACT
# =========================

@dataclass
class CandidateScore:
    candidate_id: str

    technical_score: float = 0.0
    experience_score: float = 0.0
    project_score: float = 0.0
    behavioral_score: float = 0.0
    education_score: float = 0.0
    culture_score: float = 0.0

    final_score: float = 0.0

    reasoning: str = ""
    debug_features: Dict[str, Any] = field(default_factory=dict)