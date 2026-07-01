from typing import Dict, List

from src.contracts import CandidateScore
from src.feature_engineering import build_features


# =========================
# WEIGHTS (JD OPTIMIZED)
# =========================

WEIGHTS = {
    "technical": 0.35,
    "experience": 0.20,
    "project": 0.15,
    "behavioral": 0.15,
    "education": 0.05,
    "culture": 0.10,
}


# =========================
# SAFE UTILS
# =========================

def clamp(x: float) -> float:
    return max(0.0, min(100.0, float(x or 0.0)))


# =========================
# CORE SCORERS
# =========================

def technical_score(f: Dict) -> float:
    score = (
        f.get("ml_alignment", 0) * 0.5 +
        f.get("ranking_experience", 0) * 0.3 +
        f.get("data_eng_score", 0) * 0.2 +
        f.get("skill_strength", 0) * 0.3
    )
    return clamp(score / 2)


def experience_score(f: Dict) -> float:
    score = f.get("experience_depth", 0)

    text = f.get("combined_text", "").lower()

    if any(k in text for k in ["spark", "kafka", "airflow", "pipeline"]):
        score += 15

    if any(k in text for k in ["ranking", "retrieval", "search"]):
        score += 20

    if "marketing manager" in text and "ai" in text:
        score -= 10

    return clamp(score)


def project_score(f: Dict) -> float:
    text = f.get("combined_text", "").lower()
    score = 0

    if "kaggle" in text:
        score += 25

    if any(k in text for k in ["retrieval", "ranking system", "search system"]):
        score += 40

    if any(k in text for k in ["llm", "fine-tuning", "bert"]):
        score += 20

    if any(k in text for k in ["spark", "kafka", "airflow"]):
        score += 15

    return clamp(score)


def behavioral_score(f: Dict) -> float:
    score = f.get("activity_score", 0) * 0.6

    if f.get("open_to_work", False):
        score += 15

    if f.get("recruiter_response_rate", 0) > 0.5:
        score += 10

    if f.get("activity_score", 0) < 10:
        score -= 10

    return clamp(score)


def education_score(f: Dict) -> float:
    cand = f.get("raw_candidate", None)

    if not cand:
        return 10

    edu = getattr(cand, "education", [])

    score = 10

    for e in edu:
        inst = (getattr(e, "institution", "") or "").lower()
        tier = (getattr(e, "tier", "") or "").lower()

        if "iit" in inst:
            score += 40
        elif "tier_1" in tier:
            score += 25
        elif "tier_2" in tier:
            score += 15
        else:
            score += 5

    return clamp(score)


def culture_score(f: Dict) -> float:
    score = 10

    if f.get("willing_to_relocate", False):
        score += 15

    if f.get("activity_score", 0) > 50:
        score += 15

    if f.get("profile_completeness", 0) > 80:
        score += 10

    return clamp(score)


# =========================
# REASONING ENGINE
# =========================

def generate_reasoning(cid: str, f: Dict, scores: Dict) -> str:
    reasons = []

    if scores["technical"] > 70:
        reasons.append("strong technical alignment with ML/retrieval systems")

    if f.get("ranking_experience", 0) > 30:
        reasons.append("has ranking/retrieval system exposure")

    if f.get("data_eng_score", 0) > 40:
        reasons.append("strong data engineering background")

    if f.get("activity_score", 0) > 60:
        reasons.append("high engagement and recruiter activity")

    if not reasons:
        reasons.append("moderate JD alignment based on experience and skills")

    return f"{cid}: " + "; ".join(reasons)


# =========================
# MAIN SCORER
# =========================

def score_candidate(preprocessed: Dict) -> CandidateScore:

    features = build_features(preprocessed)

    t = technical_score(features)
    e = experience_score(features)
    p = project_score(features)
    b = behavioral_score(features)
    edu = education_score(features)
    c = culture_score(features)

    final = (
        t * WEIGHTS["technical"] +
        e * WEIGHTS["experience"] +
        p * WEIGHTS["project"] +
        b * WEIGHTS["behavioral"] +
        edu * WEIGHTS["education"] +
        c * WEIGHTS["culture"]
    )

    scores = {
        "technical": t,
        "experience": e,
        "project": p,
        "behavioral": b,
        "education": edu,
        "culture": c,
    }

    reasoning = generate_reasoning(
        preprocessed.get("candidate_id", ""),
        features,
        scores
    )

    return CandidateScore(
        candidate_id=preprocessed.get("candidate_id", ""),
        technical_score=t,
        experience_score=e,
        project_score=p,
        behavioral_score=b,
        education_score=edu,
        culture_score=c,
        final_score=clamp(final),
        reasoning=reasoning,
        debug_features=features
    )


# =========================
# BATCH SCORING
# =========================

def score_all(preprocessed_list: List[Dict]) -> List[CandidateScore]:
    results = []

    for p in preprocessed_list:
        try:
            results.append(score_candidate(p))
        except Exception as e:
            print(f"[SCORER_ERROR] {p.get('candidate_id')} -> {e}")

    return results