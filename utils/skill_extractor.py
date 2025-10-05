import pandas as pd
import ast
import re 

# extract and clean skills 
def extract_skills_from_occupation_data(): 
    # load data
    skills_df = pd.read_csv("data/raw_data/occupations_data.csv")

    # extract all unique skills from the technology_skills column
    all_skills = []
    for skills in skills_df["technology_skills"].dropna():
        try:
            parsed = ast.literal_eval(skills)  # convert string list to actual list
            all_skills.extend([s.lower() for s in parsed])
        except:
            continue

    all_skills = list(set(all_skills))  # unique skills
    return all_skills 

# build regex patterns for each skill 
# add small tolerance for plurals or endings (e.g., s, es, ing) 
def build_regex_patterns(all_skills):
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
    
    return skill_patterns

ALL_SKILLS = extract_skills_from_occupation_data()
SKILL_PATTERNS = build_regex_patterns(ALL_SKILLS)

# find skills in description 
def extract_skills(description):
    if pd.isna(description):
        return []
    desc = description.lower()

    matched = [skill for skill, pattern in SKILL_PATTERNS.items() if pattern.search(desc)]
    print(f"Description: {desc[:30]}... Matched: {matched}")
    return matched