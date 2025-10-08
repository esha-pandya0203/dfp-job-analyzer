import pandas as pd
import ast
import re
import os

# === CONFIG ===
skills_file = "/Users/fathimasumreen/indeed_scraper/indeed_scraper_2/occupations_data.csv"
input_file = "/Users/fathimasumreen/indeed_scraper/Aplify_Scraper/linkedIn_jobs.csv"
output_file = "/Users/fathimasumreen/indeed_scraper/Aplify_Scraper/skills_matched_linkedin_jobs.csv"

# === LOAD SKILLS DATA ===
skills_df = pd.read_csv(skills_file)

# Extract and clean all skills from the 'technology_skills' column
all_skills = []
for skills in skills_df["technology_skills"].dropna():
    try:
        parsed = ast.literal_eval(skills)
        all_skills.extend([s.lower().strip() for s in parsed])
    except Exception:
        continue

all_skills = list(set(all_skills))  # unique skills list

# === BUILD REGEX PATTERNS ===
skill_patterns = {}
for skill in all_skills:
    escaped = re.escape(skill)
    if len(skill) <= 2:
        pattern = re.compile(rf'\b{escaped}\b', re.IGNORECASE)
    else:
        pattern = re.compile(rf'\b{escaped}(?:s|es|ing)?\b', re.IGNORECASE)
    skill_patterns[skill] = pattern

# === DEFINE EXTRACTION FUNCTION ===
def extract_skills(description):
    if pd.isna(description):
        return []
    desc = description.lower()
    matched = [skill for skill, pattern in skill_patterns.items() if pattern.search(desc)]
    return matched

# === LOAD JOB DATA ===
print(f"🔍 Reading {input_file} ...")
jobs_df = pd.read_csv(input_file)

if "description" not in jobs_df.columns:
    raise ValueError("❌ 'description' column not found in the input file.")

# === APPLY SKILL EXTRACTION ===
print("🧠 Extracting matched skills from job descriptions...")
jobs_df["Matched_Skills"] = jobs_df["description"].apply(extract_skills)

# === SAVE OUTPUT ===
jobs_df.to_csv(output_file, index=False)
print(f"✅ Done! Saved results to: {output_file}")
print(f"Total jobs processed: {len(jobs_df)}")
