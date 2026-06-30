import re
from typing import List, Dict

from src.contracts import Candidate, Skill


# =========================
# TEXT CLEANING UTIL
# =========================

def clean_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)          # remove extra spaces
    text = re.sub(r"[^\w\s\+\#\.\-]", "", text)  # keep useful tech symbols
    return text


# =========================
# SKILL NORMALIZATION
# =========================

def normalize_skill_name(name: str) -> str:
    if not name:
        return ""

    name = name.lower().strip()
    name = re.sub(r"\s+", " ", name)

    # unify common variations
    replacements = {
        "ml": "machine learning",
        "ai": "artificial intelligence",
        "llms": "llm",
        "gpt": "llm",
        "k8s": "kubernetes",
    }

    return replacements.get(name, name)


def clean_skills(skills: List[Skill]) -> List[Skill]:
    seen = set()
    cleaned = []

    for s in skills:
        norm_name = normalize_skill_name(s.name)

        if not norm_name or norm_name in seen:
            continue

        seen.add(norm_name)

        cleaned.append(
            Skill(
                name=norm_name,
                proficiency=s.proficiency,
                endorsements=s.endorsements,
                duration_months=s.duration_months
            )
        )

    return cleaned


# =========================
# EXPERIENCE BUCKETING
# =========================

def experience_bucket(years: float) -> str:
    if years < 2:
        return "junior"
    elif years < 5:
        return "mid"
    elif years < 10:
        return "senior"
    else:
        return "staff"


# =========================
# ACTIVITY SCORE (derived)
# =========================

def compute_activity_score(signals) -> float:
    if not signals:
        return 0.0

    score = 0.0

    # recruiter engagement signals
    score += signals.profile_views_received_30d * 0.2
    score += signals.saved_by_recruiters_30d * 1.0
    score += signals.search_appearance_30d * 0.05

    # responsiveness
    score += signals.recruiter_response_rate * 50

    # interview behavior
    score += signals.interview_completion_rate * 30

    # penalties
    if signals.avg_response_time_hours > 200:
        score -= 10

    if signals.open_to_work_flag:
        score += 10

    return max(0.0, min(100.0, score))


# =========================
# MAIN PREPROCESSOR
# =========================

def preprocess_candidate(candidate: Candidate) -> Dict:
    """
    Converts Candidate → feature-ready dict
    """

    profile = candidate.profile
    signals = candidate.redrob_signals

    return {
        "candidate_id": candidate.candidate_id,

        # ---------------------
        # TEXT FEATURES
        # ---------------------
        "headline_clean": clean_text(profile.headline),
        "summary_clean": clean_text(profile.summary),

        # ---------------------
        # STRUCTURAL FEATURES
        # ---------------------
        "years_experience": profile.years_of_experience,
        "experience_bucket": experience_bucket(profile.years_of_experience),

        "current_title": clean_text(profile.current_title),
        "current_industry": clean_text(profile.current_industry),

        # ---------------------
        # SKILLS
        # ---------------------
        "skills": clean_skills(candidate.skills),
        "skill_count": len(candidate.skills),

        # ---------------------
        # LOCATION SIGNALS
        # ---------------------
        "country": profile.country,
        "location": profile.location,

        # ---------------------
        # SIGNALS (IMPORTANT FOR RANKING)
        # ---------------------
        "activity_score": compute_activity_score(signals),
        "profile_completeness": getattr(signals, "profile_completeness_score", 0),

        "recruiter_response_rate": getattr(signals, "recruiter_response_rate", 0),
        "notice_period_days": getattr(signals, "notice_period_days", 0),

        "open_to_work": getattr(signals, "open_to_work_flag", False),
        "willing_to_relocate": getattr(signals, "willing_to_relocate", False),

        # ---------------------
        # RAW PASS-THROUGH (for scorers)
        # ---------------------
        "raw_candidate": candidate
    }


# =========================
# BATCH PROCESSING
# =========================

def preprocess_all(candidates: List[Candidate]) -> List[Dict]:
    return [preprocess_candidate(c) for c in candidates]