#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill Matcher
=============

A utility for matching skills from job descriptions with occupation data.

Author: Fan Yang (CMU)
Version: 1.0
"""

import pandas as pd
import ast
import os

class SkillMatcher:
    """Match skills from job descriptions"""
    
    def __init__(self):
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_skills_data(self, skills_file=None):
        """Load skills data from occupations file"""
        if skills_file is None:
            skills_file = os.path.join(self.data_dir, "raw_data_project", "occupations_data.csv")
        
        if not os.path.exists(skills_file):
            print(f"⚠️ Skills file not found: {skills_file}")
            return []
        
        try:
            skills_df = pd.read_csv(skills_file)
            all_skills = []
            
            for skills in skills_df["technology_skills"].dropna():
                try:
                    parsed = ast.literal_eval(skills)  # convert string list to actual list
                    all_skills.extend([s.lower() for s in parsed])
                except:
                    continue
            
            return list(set(all_skills))  # unique skills
        except Exception as e:
            print(f"Error loading skills data: {e}")
            return []
    
    def extract_skills(self, description, all_skills):
        """Extract skills from job description"""
        if pd.isna(description):
            return []
        desc = description.lower()
        return [skill for skill in all_skills if skill in desc]
    
    def match_skills_to_jobs(self, jobs_file, skills_file=None, output_file=None):
        """Match skills to job postings"""
        if not os.path.exists(jobs_file):
            print(f"⚠️ Jobs file not found: {jobs_file}")
            return False
        
        # Load skills data
        all_skills = self.load_skills_data(skills_file)
        if not all_skills:
            print("⚠️ No skills data available")
            return False
        
        # Load jobs data
        jobs_df = pd.read_csv(jobs_file)
        
        # Apply skill matching
        jobs_df["Matched_Skills"] = jobs_df["description"].apply(
            lambda desc: self.extract_skills(desc, all_skills)
        )
        
        # Save results
        if output_file is None:
            base_name = os.path.splitext(os.path.basename(jobs_file))[0]
            output_file = f"{base_name}_with_skills.csv"
        
        output_path = os.path.join(self.data_dir, output_file)
        jobs_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        print(f"✅ Skills matched and saved to {output_path}")
        return True
    
    def process_all_job_files(self):
        """Process all job files in the data directory"""
        job_files = []
        
        # Find all job posting files
        for file in os.listdir(self.data_dir):
            if file.startswith("Main Job Postings data") and file.endswith(".csv"):
                job_files.append(os.path.join(self.data_dir, file))
        
        if not job_files:
            print("⚠️ No job posting files found")
            return False
        
        success_count = 0
        for job_file in job_files:
            print(f"\n🔄 Processing {job_file}...")
            if self.match_skills_to_jobs(job_file):
                success_count += 1
        
        print(f"\n🎉 Successfully processed {success_count}/{len(job_files)} files")
        return success_count > 0
