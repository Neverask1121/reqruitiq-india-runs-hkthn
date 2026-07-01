import json
from typing import List, Dict, Any, Optional

from src.contracts import (
    Candidate,
    Profile,
    Skill,
    Job,
    Education,
    RedrobSignals
)


# =========================
# SAFE PARSING HELPERS
# =========================

def safe_get(data: Dict, key: str, default=None):
    return data.get(key, default)


def parse_skills(skills_raw: List[Dict]) -> List[Skill]:
    if not skills_raw:
        return []

    skills = []
    for s in skills_raw:
        skills.append(
            Skill(
                name=safe_get(s, "name", ""),
                proficiency=safe_get(s, "proficiency", "beginner"),
                endorsements=int(safe_get(s, "endorsements", 0)),
                duration_months=int(safe_get(s, "duration_months", 0))
            )
        )
    return skills


def parse_education(edu_raw: List[Dict]) -> List[Education]:
    if not edu_raw:
        return []

    edu = []
    for e in edu_raw:
        edu.append(
            Education(
                institution=safe_get(e, "institution", ""),
                degree=safe_get(e, "degree", ""),
                field_of_study=safe_get(e, "field_of_study", ""),
                start_year=int(safe_get(e, "start_year", 0)),
                end_year=int(safe_get(e, "end_year", 0)),
                grade=safe_get(e, "grade", ""),
                tier=safe_get(e, "tier", "")
            )
        )
    return edu


def parse_jobs(jobs_raw: List[Dict]) -> List[Job]:
    if not jobs_raw:
        return []

    jobs = []
    for j in jobs_raw:
        jobs.append(
            Job(
                company=safe_get(j, "company", ""),
                title=safe_get(j, "title", ""),
                start_date=safe_get(j, "start_date", ""),
                end_date=safe_get(j, "end_date", None),
                duration_months=int(safe_get(j, "duration_months", 0)),
                is_current=bool(safe_get(j, "is_current", False)),
                industry=safe_get(j, "industry", ""),
                company_size=safe_get(j, "company_size", ""),
                description=safe_get(j, "description", "")
            )
        )
    return jobs


def parse_signals(signals_raw: Dict) -> Optional[RedrobSignals]:
    if not signals_raw:
        return None

    salary = safe_get(signals_raw, "expected_salary_range_inr_lpa", {}) or {}

    return RedrobSignals(
        profile_completeness_score=float(safe_get(signals_raw, "profile_completeness_score", 0.0)),
        signup_date=safe_get(signals_raw, "signup_date", ""),
        last_active_date=safe_get(signals_raw, "last_active_date", ""),
        open_to_work_flag=bool(safe_get(signals_raw, "open_to_work_flag", False)),

        profile_views_received_30d=int(safe_get(signals_raw, "profile_views_received_30d", 0)),
        applications_submitted_30d=int(safe_get(signals_raw, "applications_submitted_30d", 0)),
        recruiter_response_rate=float(safe_get(signals_raw, "recruiter_response_rate", 0.0)),
        avg_response_time_hours=float(safe_get(signals_raw, "avg_response_time_hours", 0.0)),

        connection_count=int(safe_get(signals_raw, "connection_count", 0)),
        endorsements_received=int(safe_get(signals_raw, "endorsements_received", 0)),
        notice_period_days=int(safe_get(signals_raw, "notice_period_days", 0)),

        expected_salary_range_inr_lpa={
            "min": float(safe_get(salary, "min", 0.0)),
            "max": float(safe_get(salary, "max", 0.0))
        },

        preferred_work_mode=safe_get(signals_raw, "preferred_work_mode", ""),
        willing_to_relocate=bool(safe_get(signals_raw, "willing_to_relocate", False)),

        github_activity_score=float(safe_get(signals_raw, "github_activity_score", 0.0)),

        search_appearance_30d=int(safe_get(signals_raw, "search_appearance_30d", 0)),
        saved_by_recruiters_30d=int(safe_get(signals_raw, "saved_by_recruiters_30d", 0)),

        interview_completion_rate=float(safe_get(signals_raw, "interview_completion_rate", 0.0)),
        offer_acceptance_rate=float(safe_get(signals_raw, "offer_acceptance_rate", 0.0)),

        verified_email=bool(safe_get(signals_raw, "verified_email", False)),
        verified_phone=bool(safe_get(signals_raw, "verified_phone", False)),
        linkedin_connected=bool(safe_get(signals_raw, "linkedin_connected", False)),
    )


def parse_profile(profile_raw: Dict) -> Profile:
    return Profile(
        anonymized_name=safe_get(profile_raw, "anonymized_name", ""),
        headline=safe_get(profile_raw, "headline", ""),
        summary=safe_get(profile_raw, "summary", ""),
        location=safe_get(profile_raw, "location", ""),
        country=safe_get(profile_raw, "country", ""),
        years_of_experience=float(safe_get(profile_raw, "years_of_experience", 0.0)),
        current_title=safe_get(profile_raw, "current_title", ""),
        current_company=safe_get(profile_raw, "current_company", ""),
        current_company_size=safe_get(profile_raw, "current_company_size", ""),
        current_industry=safe_get(profile_raw, "current_industry", "")
    )


# =========================
# MAIN LOADER
# =========================

def load_candidates(json_path: str) -> List[Candidate]:
    """
    Loads raw JSON file and converts into Candidate objects
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    candidates: List[Candidate] = []

    for item in data:
        try:
            candidate = Candidate(
                candidate_id=safe_get(item, "candidate_id", ""),

                profile=parse_profile(safe_get(item, "profile", {})),

                career_history=parse_jobs(safe_get(item, "career_history", [])),
                education=parse_education(safe_get(item, "education", [])),
                skills=parse_skills(safe_get(item, "skills", [])),

                certifications=safe_get(item, "certifications", []),
                languages=safe_get(item, "languages", []),

                redrob_signals=parse_signals(safe_get(item, "redrob_signals", {}))
            )

            candidates.append(candidate)

        except Exception as e:
            # IMPORTANT: don't break pipeline for one bad record
            print(f"[DATA_LOADER_ERROR] candidate skipped: {item.get('candidate_id')} -> {str(e)}")

    return candidates


# =========================
# DEBUG HELPER (OPTIONAL)
# =========================

if __name__ == "__main__":
    path = "member2/outputs/parsed_candidates.json"
    candidates = load_candidates(path)

    print(f"Loaded candidates: {len(candidates)}")
    print(candidates[0])
