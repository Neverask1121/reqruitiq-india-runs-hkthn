# Requirement Mapping

## Project

**Redrob AI – Intelligent Candidate Discovery & Ranking Challenge**

---

# Purpose

This document maps the hiring requirements extracted from the Job Description to the corresponding fields available in the candidate dataset. It serves as a bridge between the **Job Understanding Module (Member 1)** and the **Ranking Engine (Member 3)**.

---

# Requirement Mapping

| Job Requirement                                  | Priority | Candidate Schema Field(s)                                            | Why it Matters                                                       |
| ------------------------------------------------ | -------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Senior AI Engineer                               | High     | `current_job_title`, `career_history.job_title`                      | Candidate should have worked in relevant AI/ML roles.                |
| 5–9 Years Experience (Flexible)                  | High     | `years_of_experience`, `career_history.duration`                     | Quality of experience is more important than exact years.            |
| Python                                           | High     | `skills.name`, `skills.proficiency`, `skills.months_of_experience`   | Primary programming language for the role.                           |
| Embeddings                                       | High     | `skills`, `career_history.description`, `projects`                   | Core requirement for semantic search and retrieval systems.          |
| Retrieval Systems                                | High     | `career_history.description`, `projects`, `skills`                   | Essential responsibility mentioned in the JD.                        |
| Ranking Systems                                  | High     | `career_history.description`, `projects`                             | Candidates should have built or maintained ranking systems.          |
| Vector Databases                                 | High     | `skills`, `projects`                                                 | Indicates practical knowledge of modern AI search systems.           |
| Hybrid Search                                    | High     | `career_history.description`, `projects`                             | Important for intelligent candidate retrieval.                       |
| Semantic Search                                  | High     | `skills`, `career_history.description`                               | Required to understand contextual matching.                          |
| Large Language Models (LLMs)                     | High     | `skills`, `projects`, `career_history.description`                   | Experience with production LLM applications is preferred.            |
| Production ML Systems                            | High     | `career_history.description`, `projects`                             | Demonstrates ability to deploy AI systems at scale.                  |
| Evaluation Metrics (NDCG, MRR, MAP, A/B Testing) | High     | `career_history.description`, `projects`, `skills`                   | Shows understanding of ranking quality measurement.                  |
| Product Company Experience                       | High     | `career_history.company`, `career_history.industry`                  | Product engineering experience is preferred over service-only work.  |
| Search / Recommendation Domain                   | High     | `career_history.description`, `projects`                             | Directly relevant to the responsibilities in the JD.                 |
| Startup Mindset                                  | Medium   | `career_history`, `behavioral_signals`, `professional_summary`       | Indicates adaptability, ownership, and fast execution.               |
| Builder Mentality                                | Medium   | `projects`, `career_history.description`                             | Preference for engineers who build production-ready solutions.       |
| Communication Skills                             | Medium   | `behavioral_signals.recruiter_response_rate`, `professional_summary` | Helpful indicator of collaboration and responsiveness.               |
| Documentation & Collaboration                    | Medium   | `career_history.description`, `projects`                             | Shows ability to work effectively in engineering teams.              |
| GitHub Activity                                  | Medium   | `behavioral_signals.github_activity_score`                           | Reflects engineering engagement and continuous development.          |
| Skill Assessment Performance                     | Medium   | `behavioral_signals.skill_assessment_score`                          | Objective measure of technical ability.                              |
| Open to Work                                     | Medium   | `behavioral_signals.open_to_work`                                    | Indicates candidate availability.                                    |
| Recruiter Response Rate                          | Medium   | `behavioral_signals.recruiter_response_rate`                         | Helps estimate likelihood of recruiter engagement.                   |
| Last Active Date                                 | Medium   | `behavioral_signals.last_active_date`                                | Recent activity suggests active job searching.                       |
| Notice Period                                    | Medium   | `behavioral_signals.notice_period_days`                              | Shorter notice periods improve hiring readiness.                     |
| Willingness to Relocate                          | Medium   | `behavioral_signals.willing_to_relocate`                             | Relevant because the role is based in Pune/Noida.                    |
| Expected Salary                                  | Low      | `behavioral_signals.expected_salary`                                 | Useful for recruiter decision-making but not a major ranking factor. |
| Certifications                                   | Low      | `certifications`                                                     | Additional evidence of continuous learning.                          |
| Education                                        | Low      | `education.degree`, `education.field_of_study`                       | Considered, but less important than practical experience.            |
| Institution Tier                                 | Low      | `education.institution_tier`                                         | Minor supporting signal.                                             |
| Languages                                        | Low      | `languages`                                                          | Useful only if language requirements arise.                          |

---

# Positive Signals

Candidates should receive higher scores if they demonstrate:

* Strong production AI experience
* Retrieval or search system development
* Ranking or recommendation engine experience
* Python expertise
* Experience with embeddings and vector databases
* Product-based company experience
* Strong GitHub activity
* High recruiter response rate
* Open-to-work status
* Short notice period
* Startup or builder mindset
* Strong technical assessment scores

---

# Negative Signals

Candidates should receive lower scores if they exhibit:

* Research-only background without production deployment
* Only recent LLM or prompt-engineering experience
* No experience with retrieval or ranking systems
* Entire career in service-based consulting without product ownership
* Primary expertise only in Computer Vision, Robotics, or Speech
* Long notice period
* Low recruiter responsiveness
* Inactive profile
* Poor GitHub activity (when relevant)
* Career history unrelated to AI, search, or recommendation systems

---

# Key Insight

The ranking engine should **not rely on keyword matching alone**.

Instead, it should combine:

* Semantic relevance
* Career progression
* Technical depth
* Production impact
* Behavioral signals
* Candidate availability
* Product engineering experience

This mapping enables the ranking engine to interpret candidate profiles in the same way an experienced recruiter would, resulting in more accurate and explainable candidate rankings.
