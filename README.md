# Intelligent Candidate Discovery & Ranking System

## Overview

This project was developed for the Redrob India Runs Data & AI Challenge.

The objective is to build an intelligent candidate ranking system that identifies and ranks the most suitable candidates for a Senior AI Engineer position.

The system evaluates candidates using a weighted scoring framework that considers technical skills, production AI experience, role relevance, company background, activity signals, and location preference.

## Problem Statement

Given a job description and a large candidate dataset, rank candidates according to their suitability for the role.

The target role emphasizes:

* AI Engineering
* Retrieval Systems
* Ranking Systems
* NLP & LLM Applications
* Production Machine Learning
* Search & Recommendation Systems

## Methodology

### Feature Groups

1. Technical Skill Match
2. Production Experience
3. Job Title Relevance
4. Experience Level
5. Company Background
6. Activity Signals
7. Location Match

### Scoring Formula

| Feature               | Weight |
| --------------------- | ------ |
| Skill Match           | 30%    |
| Production Experience | 20%    |
| Title Relevance       | 15%    |
| Experience Match      | 10%    |
| Company Background    | 10%    |
| Location Match        | 5%     |
| Activity Signals      | 10%    |

### Candidate Activity Signals

* Open to Work
* Recruiter Response Rate
* GitHub Activity
* Profile Completeness
* Interview Completion Rate

## Workflow

1. Read candidate profiles
2. Extract profile information
3. Compute feature scores
4. Apply penalties
5. Calculate final score
6. Rank candidates
7. Select Top 100
8. Generate submission.csv

---

## Validation

The generated submission successfully passed the official validation script provided in the challenge dataset.

## Future Improvements

* Embedding-based semantic search
* Hybrid retrieval systems
* Learning-to-rank models
* Cross-encoder re-ranking
* LLM-based candidate matching
* Feedback-driven ranking optimization

## Tech Stack

* Python
* Pandas
* JSON
* Rule-Based Ranking Framework

## Author

Disha Ambhore
