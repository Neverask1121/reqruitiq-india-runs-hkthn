from typing import Dict


def generate_reasoning(candidate_id: str, features: Dict, scores: Dict) -> str:
    """
Reasoning module for explainable ranking output.
This module generates human-readable explanations for candidate scores.
"""

    reasons = []

    if scores.get("technical", 0) > 70:
        reasons.append("strong ML / ranking system alignment")

    if features.get("ranking_experience", 0) > 30:
        reasons.append("has retrieval / ranking system experience")

    if features.get("data_eng_score", 0) > 40:
        reasons.append("strong data engineering background")

    if features.get("ml_alignment", 0) > 50:
        reasons.append("good ML/AI exposure in profile")

    if features.get("activity_score", 0) > 60:
        reasons.append("high recruiter engagement and activity")

    if not reasons:
        reasons.append("moderate JD alignment based on skills and experience")

    return f"{candidate_id}: " + "; ".join(reasons)