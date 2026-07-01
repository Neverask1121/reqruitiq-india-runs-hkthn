import re
from typing import Dict, List

from src.contracts import Candidate


# =========================
# JD-FOCUSED KEYWORDS (OPTIMIZED)
# =========================

RANKING_SYSTEM_KEYWORDS = {
    "ranking", "recommendation", "recommendation system",
    "search", "retrieval", "hybrid search",
    "bm25", "vector", "embedding",
    "faiss", "milvus", "weaviate", "elasticsearch",
    "candidate matching"
}

PRODUCTION_ML_KEYWORDS = {
    "production", "deployment", "pipeline",
    "spark", "kafka", "airflow", "etl",
    "feature store", "latency", "scaling",
    "monitoring", "data pipeline"
}

DATA_KEYWORDS = {
    "spark", "kafka", "airflow", "sql", "warehouse",
    "snowflake", "bigquery", "databricks", "etl", "pipeline"
}


# =========================
# TEXT UTIL
# =========================

def tokenize(text: str) -> List[str]:
    if not text:
        return []
    return re.findall(r"[a-zA-Z\+\#\.]+", text.lower())


def keyword_score(text: str, keywords: set) -> float:
    """
    Better than intersection:
    counts partial + exact matches
    """
    if not text:
        return 0.0

    text = text.lower()
    score = 0.0

    for k in keywords:
        if k in text:
            score += 1

    return score / max(len(keywords), 1)


# =========================
# SKILL SCORING
# =========================

def skill_strength_score(skills) -> float:
    if not skills:
        return 0.0

    score = 0.0

    for s in skills:
        base = 0.0

        if s.proficiency == "advanced":
            base += 3
        elif s.proficiency == "intermediate":
            base += 2
        else:
            base += 1

        base += min(s.endorsements / 10, 2)
        base += min(s.duration_months / 12, 2)

        score += base

    return min(score, 100.0)


# =========================
# EXPERIENCE SCORE
# =========================

def experience_depth_score(years: float) -> float:
    if years <= 1:
        return 5
    elif years <= 3:
        return 20
    elif years <= 6:
        return 45
    elif years <= 10:
        return 70
    else:
        return 85


# =========================
# JD-ALIGNMENT (MOST IMPORTANT FIX)
# =========================

def ml_alignment_score(text: str, skills) -> float:
    text = (text or "").lower()

    score = 0.0

    # strong JD relevance boost
    score += keyword_score(text, RANKING_SYSTEM_KEYWORDS) * 60
    score += keyword_score(text, PRODUCTION_ML_KEYWORDS) * 35

    # skill reinforcement (stronger now)
    skill_names = {s.name.lower() for s in skills}

    for s in skill_names:
        if any(k in s for k in ["ranking", "retrieval", "search", "vector"]):
            score += 12
        if any(k in s for k in ["spark", "kafka", "airflow"]):
            score += 6

    return min(score, 100.0)


# =========================
# DATA ENGINEERING SCORE
# =========================

def data_engineering_score(text: str, skills) -> float:
    text = (text or "").lower()

    score = keyword_score(text, DATA_KEYWORDS) * 70

    skill_names = {s.name.lower() for s in skills}

    for s in skill_names:
        if s in DATA_KEYWORDS:
            score += 8

    return min(score, 100.0)


# =========================
# RANKING SYSTEM SCORE
# =========================

def ranking_experience_score(text: str, skills) -> float:
    text = (text or "").lower()

    score = keyword_score(text, RANKING_SYSTEM_KEYWORDS) * 80

    skill_names = {s.name.lower() for s in skills}

    for s in skill_names:
        if any(k in s for k in ["ranking", "retrieval", "search", "vector"]):
            score += 15

    return min(score, 100.0)


# =========================
# SIGNAL BOOST (IMPROVED)
# =========================

def signal_quality_boost(features: Dict) -> float:
    score = 0.0

    activity = features.get("activity_score", 0)

    if activity > 70:
        score += 15
    elif activity > 40:
        score += 8

    if features.get("open_to_work", False):
        score += 12

    if features.get("recruiter_response_rate", 0) > 0.5:
        score += 10

    if features.get("notice_period_days", 999) <= 30:
        score += 5

    if features.get("profile_completeness", 0) > 80:
        score += 5

    return score


# =========================
# MAIN FEATURE ENGINE
# =========================

def build_features(preprocessed: Dict) -> Dict:

    candidate: Candidate = preprocessed["raw_candidate"]

    headline = preprocessed.get("headline_clean", "")
    summary = preprocessed.get("summary_clean", "")

    combined_text = f"{headline} {summary}".strip()

    skills = preprocessed.get("skills", [])
    years = preprocessed.get("years_experience", 0)

    features = {
        "candidate_id": preprocessed["candidate_id"],

        # CORE SIGNALS
        "skill_strength": skill_strength_score(skills),
        "experience_depth": experience_depth_score(years),

        # JD ALIGNMENT (MOST IMPORTANT)
        "ml_alignment": ml_alignment_score(combined_text, skills),
        "data_eng_score": data_engineering_score(combined_text, skills),
        "ranking_experience": ranking_experience_score(combined_text, skills),

        # PREPROCESS SIGNALS
        "activity_score": preprocessed.get("activity_score", 0),
        "profile_completeness": preprocessed.get("profile_completeness", 0),
        "open_to_work": preprocessed.get("open_to_work", False),
        "willing_to_relocate": preprocessed.get("willing_to_relocate", False),

        # TEXT
        "combined_text": combined_text,

        # RAW
        "raw_candidate": candidate
    }

    features["signal_boost"] = signal_quality_boost(features)

    return features


# =========================
# BATCH ENGINE
# =========================

def build_feature_set(preprocessed_list: List[Dict]) -> List[Dict]:
    return [build_features(p) for p in preprocessed_list]