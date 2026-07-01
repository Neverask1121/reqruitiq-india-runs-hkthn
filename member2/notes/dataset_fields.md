# Dataset Fields Documentation

## Overview

The `candidates.jsonl` dataset contains one JSON object per line, where each object represents a single candidate profile. Every candidate contains personal information, work experience, education, skills, certifications, languages, and RedRob behavioral signals used for intelligent ranking.

---

# Top-Level Fields

## 1. candidate_id

**Type:** String

**Purpose:**
Unique identifier assigned to every candidate. This field is used for referencing candidates and generating the final submission.

**Example:**

```
CAND_0000001
```

---

## 2. profile

**Type:** Dictionary (Object)

**Purpose:**
Stores the candidate's general profile information.

### Fields

* anonymized_name
* headline
* summary
* location
* country
* years_of_experience
* current_title
* current_company
* current_company_size
* current_industry

**Example Information**

* Candidate Name
* Professional Headline
* Career Summary
* Years of Experience
* Current Company
* Industry
* Location

---

## 3. career_history

**Type:** List of Dictionaries

**Purpose:**
Contains the complete employment history of the candidate.

Each job entry contains:

* company
* title
* start_date
* end_date
* duration_months
* is_current
* industry
* company_size
* description

This field is useful for:

* Career progression
* Job stability
* Domain experience
* Total experience
* Promotion analysis

---

## 4. education

**Type:** List of Dictionaries

**Purpose:**
Stores academic qualifications.

Each education entry contains:

* institution
* degree
* field_of_study
* start_year
* end_year
* grade
* tier

Useful for evaluating educational background and institution quality.

---

## 5. skills

**Type:** List of Dictionaries

**Purpose:**
Stores every technical and professional skill possessed by the candidate.

Each skill contains:

* name
* proficiency
* endorsements
* duration_months

Example:

```
Skill Name:
Python

Proficiency:
Advanced

Experience:
36 Months

Endorsements:
42
```

Useful for:

* Technical skill matching
* Experience estimation
* Skill ranking
* Candidate expertise analysis

---

## 6. certifications

**Type:** List

**Purpose:**
Stores professional certifications obtained by the candidate.

Possible examples:

* AWS
* Google Cloud
* Azure
* TensorFlow
* Data Analytics

Some candidates may have an empty certification list.

---

## 7. languages

**Type:** List of Dictionaries

**Purpose:**
Stores languages known by the candidate.

Each language contains:

* language
* proficiency

Useful for multilingual job requirements.

---

## 8. redrob_signals

**Type:** Dictionary

**Purpose:**
Stores behavioral, recruiter, and platform engagement signals that help improve candidate ranking.

### Available Signals

* profile_completeness_score
* signup_date
* last_active_date
* open_to_work_flag
* profile_views_received_30d
* applications_submitted_30d
* recruiter_response_rate
* avg_response_time_hours
* skill_assessment_scores
* connection_count
* endorsements_received
* notice_period_days
* expected_salary_range_inr_lpa
* preferred_work_mode
* willing_to_relocate
* github_activity_score
* search_appearance_30d
* saved_by_recruiters_30d
* interview_completion_rate
* offer_acceptance_rate
* verified_email
* verified_phone
* linkedin_connected

These signals provide valuable information about:

* Candidate engagement
* Recruiter interest
* Availability
* Technical credibility
* Hiring probability
* Platform activity

---

# Dataset Summary

The dataset combines traditional resume information with behavioral signals, making it richer than a standard resume dataset.

The most important sections for candidate ranking are:

1. Profile
2. Career History
3. Skills
4. RedRob Signals

These sections will form the primary input for the candidate ranking engine developed in later stages of the project.

---

# Day 1 Conclusion

Successfully completed:

* Understood the dataset structure.
* Explored the first candidate record.
* Identified all top-level dataset fields.
* Understood nested objects and lists.
* Explored profile attributes.
* Explored career history structure.
* Explored skills structure.
* Explored RedRob behavioral signals.
* Prepared the dataset for parsing and feature engineering in Day 2.
