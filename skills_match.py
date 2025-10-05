import pandas as pd
import ast
import re

# --- Load Data ---
skills_df = pd.read_csv("/Users/fathimasumreen/indeed_scraper/indeed_scraper_2/occupations_data.csv")
jobs_df = pd.read_csv("/Users/fathimasumreen/indeed_scraper/indeed_scraper_2/Main Job Postings data - Software Quality Assurance Analysts and Testers.csv")

# --- Extract and Clean Skills ---
all_skills = []
for skills in skills_df["technology_skills"].dropna():
    try:
        parsed = ast.literal_eval(skills)  # convert string list to actual list
        all_skills.extend([s.lower().strip() for s in parsed])
    except:
        continue

all_skills = list(set(all_skills))  # unique skills

# --- Build regex patterns for each skill ---
# Add small tolerance for plurals or endings (e.g., s, es, ing)
skill_patterns = {}
for skill in all_skills:
    escaped = re.escape(skill)
    # Handle short skills (like "r", "c", "go") carefully: exact word only
    if len(skill) <= 2:
        pattern = re.compile(rf'\b{escaped}\b', re.IGNORECASE)
    else:
        # For longer skills, allow simple endings like plural "s" or "es"
        pattern = re.compile(rf'\b{escaped}(?:s|es|ing)?\b', re.IGNORECASE)
    skill_patterns[skill] = pattern

# --- Function to extract skills from job description ---
def extract_skills(description):
    if pd.isna(description):
        return []
    desc = description.lower()
    matched = [skill for skill, pattern in skill_patterns.items() if pattern.search(desc)]
    return matched

# --- Apply to jobs ---
jobs_df["Matched_Skills"] = jobs_df["description"].apply(extract_skills)

# --- Save output ---
jobs_df.to_csv("Jobs_with_Matched_Skills_QA.csv", index=False)

print("✅ Done! Saved as CSV with matched skills.")
