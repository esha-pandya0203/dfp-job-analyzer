import pandas as pd
import ast

# Load data
skills_df = pd.read_csv("/Users/fathimasumreen/indeed_scraper/indeed_scraper_2/occupations_data.csv")
jobs_df = pd.read_csv("/Users/fathimasumreen/indeed_scraper/indeed_scraper_2/Main Job Postings data - Computer Network Architects.csv")

# Extract all unique skills from the technology_skills column
all_skills = []
for skills in skills_df["technology_skills"].dropna():
    try:
        parsed = ast.literal_eval(skills)  # convert string list to actual list
        all_skills.extend([s.lower() for s in parsed])
    except:
        continue

all_skills = list(set(all_skills))  # unique skills

# Function to find skills in description
def extract_skills(description):
    if pd.isna(description):
        return []
    desc = description.lower()
    return [skill for skill in all_skills if skill in desc]

# Apply to jobs
jobs_df["Matched_Skills"] = jobs_df["description"].apply(extract_skills)

# Save results
jobs_df.to_csv("Jobs_with_Matched_Skills_Network.csv", index=False)

print("✅ Done! Saved as Jobs_with_Matched_Skills.csv")
