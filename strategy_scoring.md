# Scoring Strategy

## Project

**Redrob AI – Intelligent Candidate Discovery & Ranking Challenge**

---

# Purpose

This document defines the scoring framework for evaluating and ranking candidates against the provided job description.

The objective is to move beyond simple keyword matching and score candidates based on technical expertise, relevant experience, production impact, behavioral signals, and overall suitability for the role.

The total candidate score is **100 points**.

---

# Overall Scoring Distribution

| Category                   | Weight   |
| -------------------------- | -------- |
| Technical Skills           | **35%**  |
| Relevant Experience        | **25%**  |
| Career & Project Relevance | **15%**  |
| Behavioral Signals         | **15%**  |
| Education & Certifications | **5%**   |
| Culture Fit & Soft Skills  | **5%**   |
| **Total**                  | **100%** |

---

# 1. Technical Skills (35%)

Technical capability is the most important factor for this role.

### Mandatory Skills

Candidates should be rewarded for demonstrating experience in:

* Python
* Embeddings
* Retrieval Systems
* Ranking Systems
* Vector Databases
* Semantic Search
* Large Language Models
* Production Machine Learning

### Scoring Guidelines

* Matches most mandatory skills → High score
* Demonstrates practical production experience → Additional score
* Only mentions frameworks without relevant work experience → Lower score

---

# 2. Relevant Experience (25%)

The quality of experience is more important than the number of years.

The ranking engine should evaluate:

* Experience building production AI systems
* Search or recommendation systems
* Product engineering
* Retrieval or ranking platforms
* AI infrastructure

### Positive Signals

* Product-based company experience
* Increasing responsibility
* Ownership of AI systems

### Negative Signals

* Research-only background
* Consulting experience without product ownership
* Experience unrelated to AI or search systems

---

# 3. Career & Project Relevance (15%)

Candidates should be rewarded for solving problems similar to the job requirements.

High-value projects include:

* Search engines
* Recommendation systems
* Candidate ranking
* Semantic search
* AI-powered retrieval
* Production LLM applications

Projects demonstrating measurable business impact should receive additional credit.

---

# 4. Behavioral Signals (15%)

Behavioral signals indicate how likely a candidate is to be a successful hire.

Important signals include:

### Availability

* Open to Work
* Recent platform activity
* Short notice period

### Recruiter Engagement

* High recruiter response rate
* Fast response time
* Profile viewed by recruiters

### Technical Engagement

* GitHub activity
* Skill assessment scores

Candidates showing high engagement and availability should receive higher scores.

---

# 5. Education & Certifications (5%)

Education supports the evaluation but should not dominate it.

### Education

Relevant degrees include:

* Computer Science
* Artificial Intelligence
* Data Science
* Machine Learning

### Certifications

Useful examples:

* AWS
* Google Cloud
* Azure AI
* TensorFlow
* Machine Learning certifications

Education and certifications should be considered bonus signals rather than primary decision factors.

---

# 6. Culture Fit & Soft Skills (5%)

The ideal engineer demonstrates:

* Ownership
* Product thinking
* Adaptability
* Collaboration
* Communication
* Fast learning
* Builder mindset

Candidates who have repeatedly delivered production systems and adapted to changing environments should receive higher scores.

---

# Positive Scoring Signals

The ranking engine should increase scores when candidates demonstrate:

* Strong Python expertise
* Production AI experience
* Retrieval or ranking system development
* Embeddings and vector database knowledge
* Product company experience
* High GitHub activity
* High recruiter response rate
* Open-to-work status
* Short notice period
* Strong technical assessments
* Continuous career progression
* Startup or builder mindset

---

# Negative Scoring Signals

The ranking engine should reduce scores for candidates with:

* Research-only experience
* No production deployments
* Only recent LLM or prompt engineering experience
* No retrieval or ranking experience
* Service-only consulting background without ownership
* Long notice period
* Low recruiter engagement
* Inactive profile
* Experience unrelated to AI, search, or recommendation systems

---

# Ranking Philosophy

The ranking engine should prioritize **overall suitability**, not keyword frequency.

Candidates should be evaluated using:

* Semantic understanding of their experience
* Career progression
* Production impact
* Technical depth
* Behavioral indicators
* Alignment with the job description

A candidate who has built real-world AI search systems should rank higher than a candidate who simply lists many AI technologies without relevant experience.

---

# Final Scoring Formula

```
Final Score =
(Technical Skills × 0.35)
+ (Relevant Experience × 0.25)
+ (Career & Project Relevance × 0.15)
+ (Behavioral Signals × 0.15)
+ (Education & Certifications × 0.05)
+ (Culture Fit & Soft Skills × 0.05)
```

---

# Recommendation for the Ranking Engine

Instead of filtering candidates solely by matching keywords, the ranking engine should combine structured profile data, career history, semantic relevance, and behavioral signals to produce an explainable ranking that reflects how an experienced recruiter would evaluate candidates.
