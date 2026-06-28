# AI Recruiter – Intelligent Candidate Discovery & Ranking

> **India Runs Data & AI Challenge**

An AI-powered recruitment system that intelligently understands job requirements, processes over **100,000 candidate profiles**, leverages behavioral signals, and generates an explainable ranked shortlist of the best-fit candidates.

---

# Team

| Member   | Name                | Responsibility                             |
| -------- | ------------------- | ------------------------------------------ |
| Member 1 | **Shravani Baral**  | Job Understanding & Requirement Extraction |
| Member 2 | **Aditya Bhandari** | Candidate Data Processing & Preprocessing  |
| Member 3 | **Anshu**           | Frontend Dashboard & System Integration    |
| Member 4 | **Prerana Mahajan** | AI Ranking Engine & Candidate Scoring      |

---

# Problem Statement

Traditional Applicant Tracking Systems (ATS) rely heavily on keyword matching, often missing qualified candidates.

Our solution aims to:

* Understand complex Job Descriptions.
* Perform contextual and semantic candidate matching.
* Integrate profile information, career history and behavioral signals.
* Rank candidates intelligently.
* Produce explainable hiring recommendations.

---

# Dataset

The challenge provides:

* `job_description.docx`
* `candidates.jsonl` (~100,000 candidates)
* `candidate_schema.json`
* `redrob_signals_doc.docx`
* `sample_candidates.json`
* `sample_submission.csv`
* `submission_spec.docx`
* `validate_submission.py`

---

# System Architecture

```text
                    Job Description
                           │
                           ▼
         Member 1 - Job Understanding Module
                           │
                           ▼
         Structured Job Requirement JSON
                           │
                           ▼
      Member 2 - Candidate Processing Module
                           │
                           ▼
         Parsed & Clean Candidate Dataset
                           │
                           ▼
          Member 4 - AI Ranking Engine
                           │
                           ▼
             Ranked Candidate Shortlist
                           │
                           ▼
                  submission.csv
                           │
                           ▼
     Member 3 - Recruiter Dashboard
```

---

# Team Responsibilities

## Member 1 – Shravani Baral

### Job Understanding

Responsibilities

* Analyze Job Description
* Extract Role
* Extract Required Skills
* Extract Preferred Skills
* Extract Experience
* Extract Education
* Extract Soft Skills
* Identify Hidden Requirements
* Create Structured Job Requirement JSON
* Define feature importance for ranking

Deliverable

* Structured Job Requirement JSON

---

## Member 2 – Aditya Bhandari

### Candidate Processing

Responsibilities

### explore_dataset.py

* Explore dataset structure
* Understand schema
* Identify top-level fields
* Understand nested fields

### inspect_schema.py

* Scan all candidates
* Detect missing fields
* Detect optional fields
* Detect inconsistent data types

Output

```
outputs/schema_report.json
```

### parser.py

Extract

* candidate_id
* profile
* career_history
* education
* skills
* certifications
* languages
* redrob_signals

### normalizer.py

Normalize

* Skills
* Company Names
* Job Titles
* Locations
* Degrees

### validator.py

Validate

* Missing fields
* Invalid data
* Null values

### process_dataset.py

Pipeline

```
Read Dataset

↓

Parse Candidate

↓

Normalize

↓

Validate

↓

Save Parsed Dataset
```

Output

```
outputs/parsed_candidates.json
```

### dataset_statistics.py

Generate

* Total Candidates
* Average Experience
* Top Skills
* Top Companies
* Top Industries
* Top Locations
* Top Degrees
* Certification Statistics
* Language Statistics
* Skill Distribution

Output

```
outputs/dataset_statistics.json
```

---

## Member 3 – Anshu

### Frontend Dashboard

Responsibilities

* Home Page
* Upload Job Description
* Candidate Ranking Table
* Candidate Details
* Search
* Filters
* AI Summary
* Backend Integration

Deliverable

Recruiter Dashboard

---

## Member 4 – Prerana Mahajan

### AI Ranking Engine

Inputs

* Job Requirement JSON (Member 1)
* Parsed Candidate Dataset (Member 2)

Responsibilities

* Semantic Skill Matching
* Experience Matching
* Career Analysis
* Behavioral Signal Integration
* Candidate Scoring
* Explainable Ranking
* Generate Final Rankings
* Generate Submission CSV

Deliverable

```
submission.csv
```

---

# Folder Structure

```text
AI-Recruiter/

├── dataset/
│
├── member1/
│
├── member2/
│   ├── scripts/
│   ├── outputs/
│   ├── requirements.txt
│   └── README.md
│
├── member3/
│
├── member4/
│
├── frontend/
│
├── backend/
│
└── README.md
```

---

# Member 2 Pipeline

```text
explore_dataset.py
        │
        ▼
inspect_schema.py
        │
        ▼
parser.py
        │
        ▼
normalizer.py
        │
        ▼
validator.py
        │
        ▼
process_dataset.py
        │
        ▼
parsed_candidates.json
        │
        ▼
dataset_statistics.py
```

---

# Technology Stack

### Languages

* Python 3.11+
* JavaScript
* HTML
* CSS

### Backend

* Python
* FastAPI

### AI

* Gemini / OpenAI
* Sentence Transformers
* Custom Scoring Engine

### Data Processing

* JSON
* JSONL
* pathlib

### Version Control

* Git
* GitHub

---

# Coding Standards

* Modular Architecture
* Type Hints
* PEP8 Compliance
* Exception Handling
* Reusable Functions
* Memory-Efficient Processing

---

# Expected Outputs

### Member 1

* Structured Job Requirement JSON

### Member 2

```
outputs/

schema_report.json
parsed_candidates.json
dataset_statistics.json
```

### Member 4

```
submission.csv
```

### Member 3

Interactive Recruiter Dashboard

---

# Current Progress

| Member          | Status                                                |
| --------------- | ----------------------------------------------------- |
| Shravani Baral  | Job Description Analysis                              |
| Aditya Bhandari | Dataset Exploration Completed, Processing In Progress |
| Anshu           | Pending                                               |
| Prerana Mahajan | Pending                                               |

---

# Final Workflow

```text
Job Description
        │
        ▼
Job Understanding
(Member 1)
        │
        ▼
Candidate Processing
(Member 2)
        │
        ▼
AI Ranking Engine
(Member 4)
        │
        ▼
Ranked Candidates
        │
        ▼
submission.csv
        │
        ▼
Recruiter Dashboard
(Member 3)
```

---

# Future Scope

* Resume Upload Support
* AI Resume Summarization
* Candidate Comparison
* Interview Question Generation
* Bias Detection
* Skill Gap Analysis
* Salary Prediction
* Multi-Job Support
* Recruiter Chatbot

---

# Goal

Build an intelligent AI recruitment system capable of understanding hiring requirements, processing over **100,000 candidate profiles**, integrating behavioral signals, and generating an explainable, scalable, and highly accurate ranked shortlist of candidates.
