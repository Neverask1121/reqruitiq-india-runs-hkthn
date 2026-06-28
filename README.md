# Intelligent Candidate Discovery & Ranking Challenge

An AI-powered candidate ranking system built for the **Redrob Hackathon**. The project ranks 100,000 candidates against a given job description and returns the **Top 100 most relevant candidates** with explainable reasoning while satisfying the competition's compute constraints.

---

## Overview

The objective of this project is to design an intelligent candidate discovery pipeline capable of:

- Parsing structured candidate profiles
- Understanding job requirements
- Ranking candidates based on relevance
- Detecting and avoiding honeypot candidates
- Producing human-readable reasoning for every recommendation

The system is designed to operate entirely on **CPU**, within **16 GB RAM**, and complete ranking in **under 5 minutes**.

---

## Dataset

The participant bundle contains:

| File | Description |
|------|-------------|
| `candidates.jsonl.gz` | 100,000 candidate profiles |
| `sample_candidates.json` | First 50 candidates for schema inspection |
| `candidate_schema.json` | Complete JSON schema |
| `job_description.md` | Target job description |
| `redrob_signals_doc.md` | Documentation for behavioral signals |
| `submission_spec.md` | Competition rules and submission format |
| `submission_metadata_template.yaml` | Submission metadata template |
| `sample_submission.csv` | Submission format example |
| `validate_submission.py` | Submission validator |

---

# Project Structure

```text
.
├── data/
│   ├── candidates.jsonl.gz
│   ├── sample_candidates.json
│   ├── candidate_schema.json
│   └── job_description.md
│
├── src/
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── ranker.py
│   ├── scorer.py
│   ├── reasoning.py
│   └── utils.py
│
├── outputs/
│   └── submission.csv
│
├── notebooks/
│
├── validate_submission.py
├── requirements.txt
└── README.md
```

---

# Ranking Pipeline

```
Candidate Dataset
        │
        ▼
Data Loading
        │
        ▼
Data Cleaning
        │
        ▼
Feature Engineering
        │
        ▼
Behavioral Signal Analysis
        │
        ▼
Job Description Encoding
        │
        ▼
Similarity Scoring
        │
        ▼
Weighted Ranking
        │
        ▼
Honeypot Detection
        │
        ▼
Top 100 Selection
        │
        ▼
Reason Generation
        │
        ▼
Submission CSV
```

---

# Features

- Structured candidate parsing
- Job-description-aware ranking
- Behavioral signal scoring
- Multi-factor weighted ranking
- Explainable recommendations
- Honeypot detection
- Fast CPU inference
- Submission validation

---

# Installation

Clone the repository

```bash
git clone https://github.com/yourusername/redrob-hackathon.git

cd redrob-hackathon
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Running

If using the compressed dataset:

```python
import gzip
import json

with gzip.open("candidates.jsonl.gz","rt") as f:
    candidates = [json.loads(line) for line in f]

print(len(candidates))
```

Or unzip first

```bash
gunzip -k candidates.jsonl.gz
```

---

# Generate Rankings

```bash
python src/ranker.py
```

The output will be generated as

```
outputs/submission.csv
```

---

# Validate Submission

```bash
python validate_submission.py outputs/submission.csv
```

---

# Submission Format

The generated CSV should contain:

| Column | Description |
|----------|-------------|
| rank | Candidate rank |
| candidate_id | Candidate identifier |
| reasoning | 1–2 sentence explanation |

Only the **Top 100** candidates should be included.

---

# Compute Constraints

- CPU Only
- No Internet Access
- Maximum Runtime: 5 Minutes
- Maximum Memory: 16 GB RAM

---

# Evaluation

Submissions are evaluated on multiple stages including:

- Ranking Quality
- Generalization
- Behavioral Signal Usage
- Honeypot Avoidance
- Explainability
- Robustness

A honeypot rate greater than **10%** in the Top 100 results in disqualification.

---

# Technologies

- Python
- Pandas
- NumPy
- Scikit-learn
- Sentence Transformers (optional)
- JSON
- CSV

---

# Future Improvements

- Hybrid semantic retrieval
- Learning-to-rank models
- Better behavioral embeddings
- Explainable AI (XAI)
- Faster vector search
- Ensemble ranking models

---

# Acknowledgements

Built for the **Redrob Intelligent Candidate Discovery & Ranking Hackathon**.

Special thanks to the Redrob team for providing the dataset, documentation, and evaluation framework.

---

# License

This repository is intended for educational and hackathon purposes.