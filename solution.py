import json
import re
import math
import os
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def find_file(filename):
    for root, dirs, files in os.walk(BASE_DIR):
        if filename in files:
            return os.path.join(root, filename)

    parent = os.path.dirname(BASE_DIR)
    for root, dirs, files in os.walk(parent):
        if filename in files:
            return os.path.join(root, filename)

    raise FileNotFoundError(f"{filename} not found")

CANDIDATES_FILE = find_file("candidates.jsonl")
OUTPUT_FILE = os.path.join(os.path.dirname(CANDIDATES_FILE), "submission.csv")

TARGET_SKILLS = {
    "python", "machine learning", "ml", "ai", "nlp", "llm", "llms",
    "embeddings", "embedding", "retrieval", "ranking", "search",
    "recommendation", "recommender", "vector database", "vector db",
    "faiss", "pinecone", "qdrant", "weaviate", "milvus",
    "elasticsearch", "opensearch", "sentence-transformers",
    "bge", "e5", "fine-tuning", "lora", "qlora", "peft",
    "ndcg", "mrr", "map", "a/b testing", "ab testing",
    "learning to rank", "xgboost"
}

GOOD_TITLES = [
    "ml engineer", "machine learning engineer", "ai engineer",
    "nlp engineer", "search engineer", "ranking engineer",
    "recommendation engineer", "recommender", "data scientist",
    "applied scientist", "backend engineer"
]

BAD_TITLES = [
    "marketing", "hr", "recruiter", "sales", "content writer",
    "designer", "accountant", "operations"
]

SERVICE_COMPANIES = [
    "tcs", "infosys", "wipro", "accenture", "cognizant",
    "capgemini", "mindtree", "tech mahindra", "hcl"
]

GOOD_LOCATIONS = [
    "pune", "noida", "delhi", "gurgaon", "gurugram",
    "mumbai", "hyderabad", "bengaluru", "bangalore"
]

def clean_text(x):
    if x is None:
        return ""
    return str(x).lower()

def keyword_score(text, keywords):
    text = clean_text(text)
    hits = sum(1 for k in keywords if k in text)
    return min(hits / 15, 1.0), hits

def get_all_text(candidate):
    parts = []

    profile = candidate.get("profile", {})
    parts += [
        profile.get("headline", ""),
        profile.get("summary", ""),
        profile.get("current_title", ""),
        profile.get("current_company", ""),
        profile.get("current_industry", ""),
        profile.get("location", "")
    ]

    for job in candidate.get("career_history", []):
        parts += [
            job.get("title", ""),
            job.get("company", ""),
            job.get("industry", ""),
            job.get("description", "")
        ]

    for skill in candidate.get("skills", []):
        if isinstance(skill, dict):
            parts.append(skill.get("name", ""))
        else:
            parts.append(str(skill))

    for edu in candidate.get("education", []):
        parts += [
            edu.get("degree", ""),
            edu.get("field_of_study", ""),
            edu.get("institution", "")
        ]

    return " ".join(parts)

def normalize(value, min_val, max_val):
    try:
        value = float(value)
    except:
        return 0
    return max(0, min((value - min_val) / (max_val - min_val), 1))

def score_candidate(c):
    profile = c.get("profile", {})
    signals = c.get("redrob_signals", {})
    text = get_all_text(c)

    years = profile.get("years_of_experience", 0)
    title = clean_text(profile.get("current_title", ""))
    company = clean_text(profile.get("current_company", ""))
    location = clean_text(profile.get("location", ""))

    skill_match, skill_hits = keyword_score(text, TARGET_SKILLS)

    title_score = 1.0 if any(t in title for t in GOOD_TITLES) else 0.0
    if any(t in title for t in BAD_TITLES):
        title_score = 0.0

    exp_score = 1.0 if 5 <= years <= 9 else 0.6 if 4 <= years <= 12 else 0.2
    location_score = 1.0 if any(loc in location for loc in GOOD_LOCATIONS) else 0.4

    product_company_score = 0.8
    if any(s in company for s in SERVICE_COMPANIES):
        product_company_score = 0.35

    production_keywords = [
        "production", "deployed", "real users", "scale", "ranking",
        "retrieval", "search", "recommendation", "recommender",
        "a/b", "ab test", "ndcg", "mrr", "map", "evaluation"
    ]
    production_score, production_hits = keyword_score(text, production_keywords)

    activity_score = 0
    activity_score += normalize(signals.get("profile_completeness_score", 0), 40, 100) * 0.20
    activity_score += normalize(signals.get("recruiter_response_rate", 0), 0, 1) * 0.25
    activity_score += normalize(signals.get("github_activity_score", 0), 0, 100) * 0.15
    activity_score += normalize(signals.get("interview_completion_rate", 0), 0, 1) * 0.15
    activity_score += 0.15 if signals.get("open_to_work_flag") else 0
    activity_score += 0.10 if signals.get("notice_period_days", 90) <= 30 else 0

    penalty = 0
    if any(bad in title for bad in BAD_TITLES):
        penalty += 0.25
    if "research" in text and production_score < 0.2:
        penalty += 0.15
    if "langchain" in text and production_score < 0.25:
        penalty += 0.15
    if "computer vision" in text and "nlp" not in text and "retrieval" not in text:
        penalty += 0.15

    final_score = (
        skill_match * 0.30 +
        production_score * 0.20 +
        title_score * 0.15 +
        exp_score * 0.10 +
        product_company_score * 0.10 +
        location_score * 0.05 +
        activity_score * 0.10
    )

    final_score = max(0, min(final_score - penalty, 1))

    reasoning = (
        f"{profile.get('current_title', 'Candidate')} with {years} yrs; "
        f"{skill_hits} JD skill matches; "
        f"{production_hits} production/ranking signals; "
        f"location={profile.get('location', '')}; "
        f"response_rate={signals.get('recruiter_response_rate', 0)}; "
        f"open_to_work={signals.get('open_to_work_flag', False)}."
    )

    return final_score, reasoning

def main():
    results = []

    print("Reading:", CANDIDATES_FILE)

    with open(CANDIDATES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            candidate = json.loads(line)
            score, reasoning = score_candidate(candidate)

            results.append({
                "candidate_id": candidate["candidate_id"],
                "rank": 0,
                "score": round(score, 6),
                "reasoning": reasoning[:300]
            })

    results = sorted(results, key=lambda x: x["score"], reverse=True)[:100]

    for i, row in enumerate(results, start=1):
        row["rank"] = i

    df = pd.DataFrame(results)[["candidate_id", "rank", "score", "reasoning"]]
    df.to_csv(OUTPUT_FILE, index=False)

    print("Done! Top 100 submission.csv created at:")
    print(OUTPUT_FILE)
    print(df.head(10))

if __name__ == "__main__":
    main()