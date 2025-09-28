#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Job Data Loader for Google Sheets Integration
============================================

This module loads job listing data from the team's Google Sheets
and integrates it with the existing O*NET and BLS data.

Author: Project Team
Version: 1.0
"""

import pandas as pd
import requests
import os
from datetime import datetime
import json
import sys

class JobDataLoader:
    """Load and process job listing data from Google Sheets"""
    
    def __init__(self):
        # Google Sheets URL provided by the team
        self.sheets_url = "https://docs.google.com/spreadsheets/d/1kGx-QwGAiwd1zs0PNDuVAbyN1L7V7ezDrdqKXf4Exws/edit?gid=0#gid=0"
        self.csv_export_url = "https://docs.google.com/spreadsheets/d/1kGx-QwGAiwd1zs0PNDuVAbyN1L7V7ezDrdqKXf4Exws/export?format=csv&gid=0"
        
    def load_job_data(self, use_cache=True):
        """
        Load job data from Google Sheets
        
        Args:
            use_cache (bool): Whether to use cached data if available
            
        Returns:
            pd.DataFrame: Job listing data
        """
        cache_file = "data/cached_job_data.csv"
        
        # Check if we should use cached data
        if use_cache and os.path.exists(cache_file):
            # Check if cache is recent (less than 24 hours old)
            cache_time = os.path.getmtime(cache_file)
            current_time = datetime.now().timestamp()
            
            if (current_time - cache_time) < 86400:  # 24 hours
                print("Loading cached job data...")
                return pd.read_csv(cache_file)
        
        # Try to download fresh data
        try:
            print("Downloading fresh job data from Google Sheets...")
            response = requests.get(self.csv_export_url, timeout=30)
            response.raise_for_status()
            
            # Parse CSV data
            from io import StringIO
            csv_data = StringIO(response.text)
            df = pd.read_csv(csv_data)
            
            # Save to cache
            os.makedirs("data", exist_ok=True)
            df.to_csv(cache_file, index=False)
            print(f"Job data cached to {cache_file}")
            
            return df
            
        except Exception as e:
            print(f"Error downloading job data: {e}")
            
            # Fall back to cache if available
            if os.path.exists(cache_file):
                print("Falling back to cached data...")
                return pd.read_csv(cache_file)
            
            # Fall back to mock data for testing
            print("Falling back to mock data for testing...")
            try:
                sys.path.append(os.path.dirname(__file__))
                from mock_job_data import generate_mock_job_data
                return generate_mock_job_data(100)
            except Exception as mock_error:
                print(f"Could not load mock data: {mock_error}")
                pass
            
            # Return empty DataFrame if no data available
            return pd.DataFrame()
    
    def analyze_job_data_structure(self, df):
        """Analyze the structure of the job data"""
        print("\nJob Data Structure Analysis:")
        print("=" * 50)
        
        print(f"Total records: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        
        # Check for expected columns based on project requirements
        expected_columns = [
            "Job_title", "Company", "Salary_min", "Salary_max", 
            "Skills_list", "Location", "Redirect_link", "Experience_level",
            "Apply_url", "apply_url", "ApplyURL"
        ]
        
        print("\nColumn Analysis:")
        for col in expected_columns:
            if col in df.columns:
                non_null_count = df[col].notna().sum()
                print(f"  {col}: {non_null_count}/{len(df)} records ({non_null_count/len(df)*100:.1f}%)")
            else:
                print(f"  {col}: NOT FOUND")
        
        # Show sample data
        print(f"\nSample Data:")
        print(df.head().to_string())
        
        return df
    
    def process_job_data(self, df):
        """Process and clean the job data"""
        if df.empty:
            return df
        
        processed_df = df.copy()
        
        # Clean salary data
        if 'Salary_min' in processed_df.columns:
            processed_df['Salary_min_clean'] = processed_df['Salary_min'].apply(self._clean_salary)
        
        if 'Salary_max' in processed_df.columns:
            processed_df['Salary_max_clean'] = processed_df['Salary_max'].apply(self._clean_salary)
        
        # Process skills
        if 'Skills_list' in processed_df.columns:
            processed_df['Skills_parsed'] = processed_df['Skills_list'].apply(self._parse_skills)
        
        # Add SOC code mapping
        processed_df['SOC_Code'] = processed_df['Job_title'].apply(self._map_to_soc_code)
        
        return processed_df
    
    def _clean_salary(self, salary_value):
        """Clean salary values"""
        if pd.isna(salary_value):
            return None
        
        salary_str = str(salary_value)
        
        # Remove common non-numeric characters
        import re
        salary_clean = re.sub(r'[^\d.]', '', salary_str)
        
        try:
            return float(salary_clean) if salary_clean else None
        except:
            return None
    
    def _parse_skills(self, skills_value):
        """Parse skills from string format"""
        if pd.isna(skills_value):
            return []
        
        skills_str = str(skills_value)
        
        # Handle different formats
        if skills_str.startswith('[') and skills_str.endswith(']'):
            # List format
            skills_str = skills_str.strip('[]')
            skills = [skill.strip().strip("'\"") for skill in skills_str.split(',')]
        else:
            # Comma-separated format
            skills = [skill.strip() for skill in skills_str.split(',')]
        
        return [skill for skill in skills if skill]
    
    def _map_to_soc_code(self, job_title):
        """Map job title to SOC code"""
        try:
            from utils.job_title_mapping import find_soc_code
            soc_info = find_soc_code(job_title)
            return soc_info['soc_code'] if soc_info else None
        except:
            return None
    
    def get_job_categories(self, df):
        """Get job categories from the data"""
        if 'SOC_Code' in df.columns:
            # Group by SOC code
            categories = df.groupby('SOC_Code').size().sort_values(ascending=False)
            return categories
        else:
            # Fall back to job title analysis
            if 'Job_title' in df.columns:
                return df['Job_title'].value_counts().head(20)
            return pd.Series()
    
    def get_salary_statistics(self, df):
        """Get salary statistics from the data"""
        stats = {}
        
        if 'Salary_min_clean' in df.columns:
            min_salaries = df['Salary_min_clean'].dropna()
            if len(min_salaries) > 0:
                stats['min_salary_avg'] = min_salaries.mean()
                stats['min_salary_median'] = min_salaries.median()
        
        if 'Salary_max_clean' in df.columns:
            max_salaries = df['Salary_max_clean'].dropna()
            if len(max_salaries) > 0:
                stats['max_salary_avg'] = max_salaries.mean()
                stats['max_salary_median'] = max_salaries.median()
        
        return stats
    
    def get_skills_analysis(self, df):
        """Analyze skills from job data"""
        if 'Skills_parsed' not in df.columns:
            return {}
        
        all_skills = []
        for skills_list in df['Skills_parsed']:
            if isinstance(skills_list, list):
                all_skills.extend(skills_list)
        
        if all_skills:
            skill_counts = pd.Series(all_skills).value_counts()
            return skill_counts.head(20).to_dict()
        
        return {}

def main():
    """Test the job data loader"""
    print("Job Data Loader Test")
    print("=" * 30)
    
    loader = JobDataLoader()
    
    # Load data
    df = loader.load_job_data()
    
    if df.empty:
        print("No job data available")
        return
    
    # Analyze structure
    loader.analyze_job_data_structure(df)
    
    # Process data
    processed_df = loader.process_job_data(df)
    
    # Get statistics
    categories = loader.get_job_categories(processed_df)
    salary_stats = loader.get_salary_statistics(processed_df)
    skills_analysis = loader.get_skills_analysis(processed_df)
    
    print(f"\nJob Categories:")
    print(categories)
    
    print(f"\nSalary Statistics:")
    for key, value in salary_stats.items():
        print(f"  {key}: ${value:,.0f}" if value else f"  {key}: N/A")
    
    print(f"\nTop Skills:")
    for skill, count in list(skills_analysis.items())[:10]:
        print(f"  {skill}: {count}")

if __name__ == "__main__":
    main()
