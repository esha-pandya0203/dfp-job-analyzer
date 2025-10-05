import pandas as pd
import ast

def extract_skills_from_occupation_data(): 
    # load data
    skills_df = pd.read_csv("data/raw_data/occupations_data.csv")
    # jobs_df = pd.read_csv("/Users/fathimasumreen/indeed_scraper/indeed_scraper_2/Main Job Postings data - Computer Network Architects.csv")

    # Extract all unique skills from the technology_skills column
    all_skills = []
    for skills in skills_df["technology_skills"].dropna():
        try:
            parsed = ast.literal_eval(skills)  # convert string list to actual list
            all_skills.extend([s.lower() for s in parsed])
        except:
            continue

    all_skills = list(set(all_skills))  # unique skills
    return all_skills 

# unction to find skills in description
def extract_skills(description):
    print('Extracting data')
    if pd.isna(description):
        return []
    desc = description.lower()

    all_skills = extract_skills_from_occupation_data(); 

    return [skill for skill in all_skills if skill in desc]

    # # Apply to jobs
    # jobs_df["Matched_Skills"] = jobs_df["description"].apply(extract_skills)

    # # Save results
    # jobs_df.to_csv("Jobs_with_Matched_Skills_Network.csv", index=False)

    # print("✅ Done! Saved as Jobs_with_Matched_Skills.csv")
