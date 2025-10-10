"""
------------------------------------------------------------
File: skill_extractor.py
Team: Orange Team
Members: 
    - Jiatong Li (jiatong4)
    - Esha Pandya (epandya)
    - Fan Yang (fy4)
    - Sumreen Fathima (sumreenf)

Description:
    Code to extract skills from a job listing description applied 
    along the dataframe's axis. 

Imports:
    - Imports from: streamlit, pandas, utils
    - Imported by: app.py
------------------------------------------------------------
"""

import pandas as pd
import ast
import re 
import os

def _parse_technology_skills_column(series):
    """Parse a pandas Series of technology_skills values into a flat lowercase list."""
    parsed_skills = []
    for value in series.dropna():
        try:
            # If already a list (e.g., after JSON read), keep as-is; else parse from string
            if isinstance(value, list):
                items = value
            else:
                items = ast.literal_eval(value) if isinstance(value, str) else []
            for item in items:
                if isinstance(item, str):
                    cleaned = item.strip().lower()
                    if cleaned:
                        parsed_skills.append(cleaned)
        except Exception:
            # Silently skip malformed rows
            continue
    return parsed_skills

# extract and unify skills from multiple sources (O*NET + legacy occupations_data)
def extract_skills_from_occupation_data(): 
    onet_csv_path = os.path.join("data", "ONET_Data.csv")
    legacy_csv_path = os.path.join("data", "raw_data", "occupations_data.csv")

    unified_skills = []

    # Prefer O*NET enhanced data if available
    if os.path.exists(onet_csv_path):
        try:
            onet_df = pd.read_csv(onet_csv_path)
            if "technology_skills" in onet_df.columns:
                unified_skills.extend(_parse_technology_skills_column(onet_df["technology_skills"]))
        except Exception:
            # If O*NET file is present but unreadable, fall back to legacy data as well
            pass

    # Also include legacy source if present to augment coverage
    if os.path.exists(legacy_csv_path):
        try:
            legacy_df = pd.read_csv(legacy_csv_path)
            if "technology_skills" in legacy_df.columns:
                unified_skills.extend(_parse_technology_skills_column(legacy_df["technology_skills"]))
        except Exception:
            pass

    # Deduplicate and return
    unified_skills = sorted(list(set(unified_skills)))
    return unified_skills 

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
    return matched