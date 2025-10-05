#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Loading Utilities for Pennsylvania Employment Dashboard
==========================================================

This module contains utility functions for loading and processing data.

Author: Fan Yang (CMU)
Version: 1.0
"""

import streamlit as st
import pandas as pd
import os
import re
from .job_data_loader import JobDataLoader

# Import BLS dictionary
try:
    from data.bls_dict import bls_dict
except ImportError:
    # Fallback BLS dictionary if file not found
    bls_dict = {
        '15-1251': ['AI', 'ML', 'Artificial Intelligence', 'Machine Learning', 'Generative AI', 'Gen AI', 'LLM', 'Software Engineer with Poly Mid', 'Cloud', 'IT Security', 'IT', 'Support Technician', 'IT Support', 'Product Support Engineer', 'Lead', 'Technical Support', 'Windows Engineer', 'Tech Leader', 'CIO', 'Technology Officer', 'Azure', 'AWS', 'Technology', 'Reliability Engineer', 'Customer Success Manager', 'Monitoring Center Analyst', 'Customer Success', 'SDSA', 'Site Reliability Engineer', 'CCaaS', 'IAM', 'GEN AI Architect', 'Technoogy & Innovation', 'Platform Engineer'], 
        '15-1252': ['DevOps', 'Release Manager', 'PaaS Lead', 'Platorm Infrastructure Engineer', 'RHEL Engineer', 'RHEL', 'Experienced Software Engineer', 'Software', 'Developer', 'Frontend engineer', 'Backend Engineer', 'Full Stack', 'Frontend', 'Backend', 'React'], 
        '15-1253': ['Operations', 'General Manager', 'Project Coordinator', 'Administrative Business Partner', 'Logistics', 'Customer Experience Specialist', 'Brand Manager', 'Plant Manager', 'Customer Success', 'Demand Planner', 'Workforce Management', 'Operational', 'Supply Chain', 'Coordinator', 'Extruder Area Manager', 'Administrative Assistant', 'Operating', 'Commodities', 'People, Culture, & Performance', 'Executive Assistant', 'Regional Manager', 'Assistant', 'Concierge', 'Learning & Development', 'Marketing', 'Executive', 'Customer Success', 'VP', 'Vice President', 'Field Deployment Lead', 'Warehouse Lead', 'Regional Sales', 'Store Manager', 'HR', 'Retail', 'Recruiter', 'QA', 'Quality Assurance', 'Tester', 'Quality Control'], 
        '15-2050': ['Data', 'Business Intelligence Analyst', 'Analytics', 'Analyst', 'PowerBI Developer', 'Quantitative', 'Applied Scientist', 'Machine Learning', 'Research Scientist', 'Decision Science', 'Scientist', 'AI', 'ML', 'Gen AI'], 
        '11-3021': ['Product', 'Wealth Management Analyst', ' Creative Strategist', 'UX', 'UI', 'Solutions', 'Technical Product Manager'], 
        '15-1241': ['Information Security', 'SOC', 'Cybersecurity', 'Cyber', 'Security', 'Compliance', 'Information System', 'Help Desk Support', 'Engineer, Data Center', 'Security Risk Analyst', 'IT', 'IT Support', 'Privacy', 'Incident Response', 'Data Center', 'Strategy', 'Vulnerability', 'Network', 'Threat Analyst', 'Technology and Innovation', 'Security Operations', 'Counterintelligence', 'Risk', 'Internal Audit', 'Incident', 'Threat', 'Anti-Money Laundering', 'Comply-to-Connect & Endpoint Policy Analyst'] 
    }

@st.cache_data
def load_job_data():
    """Load job data from scraper"""
    try:
        # Try to load job data from various sources
        data_files = [
            "data/Jobs_with_Matched_Skills.csv",
            "data/Jobs_with_Matched_Skills_SoftDev.csv", 
            "data/Jobs_with_Matched_Skills_DataSci.csv",
            "data/Jobs_with_Matched_Skills_CompProg.csv",
            "data/Jobs_with_Matched_Skills_Managers.csv",
            "data/Jobs_with_Matched_Skills_Network.csv",
            "data/Jobs_with_Matched_Skills_QA.csv",
            "data/Job_Data.csv",
            "data/ONET_Data.csv"
        ]
        
        for file_path in data_files:
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                if not df.empty:
                    # Clean and standardize the data
                    df = clean_job_data(df)
                    return df
        
        # If no data exists, create some mock data for demo
        st.warning("No job data found. Creating mock data for demo...")
        mock_data = create_mock_job_data()
        return mock_data
        
    except Exception as e:
        st.error(f"Error loading job data: {e}")
        return None

def create_mock_job_data():
    """Create mock job data for demonstration"""
    import pandas as pd
    
    mock_jobs = [
        {
            'title': 'Software Engineer',
            'code': '15-1252',
            'description': 'Develops, creates, and modifies general computer applications software or specialized utility programs.',
            'skills': ['Python', 'JavaScript', 'SQL', 'Git'],
            'education': 'Bachelor\'s degree in Computer Science or related field',
            'salary': '$85,000 - $120,000',
            'employment': 'High demand'
        },
        {
            'title': 'Data Scientist',
            'code': '15-2050',
            'description': 'Extracts insights from data using statistical analysis and machine learning techniques.',
            'skills': ['Python', 'R', 'Machine Learning', 'Statistics'],
            'education': 'Master\'s degree in Data Science or related field',
            'salary': '$90,000 - $130,000',
            'employment': 'Growing rapidly'
        },
        {
            'title': 'Data Analyst',
            'code': '15-2050',
            'description': 'Analyzes data to help organizations make informed business decisions.',
            'skills': ['Excel', 'SQL', 'Tableau', 'Python'],
            'education': 'Bachelor\'s degree in Business or related field',
            'salary': '$55,000 - $80,000',
            'employment': 'Steady demand'
        },
        {
            'title': 'Product Manager',
            'code': '11-3021',
            'description': 'Oversees product development and manages product lifecycle.',
            'skills': ['Project Management', 'Analytics', 'Communication', 'Strategy'],
            'education': 'Bachelor\'s degree in Business or related field',
            'salary': '$75,000 - $110,000',
            'employment': 'High demand'
        },
        {
            'title': 'UX Designer',
            'code': '27-1024',
            'description': 'Designs user experiences for digital products and services.',
            'skills': ['Figma', 'User Research', 'Prototyping', 'Design Thinking'],
            'education': 'Bachelor\'s degree in Design or related field',
            'salary': '$65,000 - $95,000',
            'employment': 'Growing field'
        }
    ]
    
    return pd.DataFrame(mock_jobs)

def clean_job_data(df):
    """Clean and standardize job data"""
    # Create a copy to avoid modifying original
    df_clean = df.copy()
    
    # Standardize column names
    column_mapping = {
        'title': 'title',
        'companyName': 'company',
        'description': 'description', 
        'location': 'location',
        'salary_min': 'salary_min',
        'salary_max': 'salary_max',
        'experienceLevel': 'experience_level',
        'Matched_Skills': 'skills',
        'Job_Category_Code': 'code'
    }
    
    # Rename columns if they exist
    for old_name, new_name in column_mapping.items():
        if old_name in df_clean.columns:
            df_clean[new_name] = df_clean[old_name]
    
    # Ensure required columns exist
    required_columns = ['title', 'description', 'skills', 'code']
    for col in required_columns:
        if col not in df_clean.columns:
            if col == 'skills':
                df_clean[col] = [[] for _ in range(len(df_clean))]
            elif col == 'code':
                df_clean[col] = '15-1251'  # Default SOC code
            else:
                df_clean[col] = 'N/A'
    
    # Clean skills column - convert string representation of list to actual list
    if 'skills' in df_clean.columns:
        def parse_skills(skills_str):
            if pd.isna(skills_str) or skills_str == 'N/A':
                return []
            if isinstance(skills_str, str):
                try:
                    # Handle string representation of list
                    import ast
                    return ast.literal_eval(skills_str)
                except:
                    # If parsing fails, split by comma
                    return [s.strip().strip("'\"") for s in skills_str.split(',')]
            return skills_str if isinstance(skills_str, list) else []
        
        df_clean['skills'] = df_clean['skills'].apply(parse_skills)
    
    # Add salary column if not exists
    if 'salary' not in df_clean.columns:
        if 'salary_min' in df_clean.columns and 'salary_max' in df_clean.columns:
            df_clean['salary'] = df_clean.apply(
                lambda row: f"${row['salary_min']} - ${row['salary_max']}" 
                if pd.notna(row['salary_min']) and pd.notna(row['salary_max']) 
                else 'Not Specified', axis=1
            )
        else:
            df_clean['salary'] = 'Not Specified'
    
    # Add education column if not exists
    if 'education' not in df_clean.columns:
        df_clean['education'] = 'Not Specified'
    
    return df_clean

@st.cache_data
def load_pa_occupation_data():
    """Load occupation data (alias for load_job_data)"""
    return load_job_data()

@st.cache_data
def load_onet_data():
    """Load O*NET occupation data"""
    try:
        # Try to load new fixed filename first
        new_file = os.path.join("data", "ONET_Data.csv")
        if os.path.exists(new_file):
            df = pd.read_csv(new_file)
            return df
        
        # Fallback to old filename pattern (search for any bls_filtered_occupations file)
        data_folder = "data"
        if os.path.exists(data_folder):
            import glob
            old_files = glob.glob(os.path.join(data_folder, "bls_filtered_occupations_*.csv"))
            if old_files:
                # Use the most recent file
                latest_file = max(old_files, key=os.path.getctime)
                df = pd.read_csv(latest_file)
                return df
        
        st.warning("No O*NET data file found")
        return None
    except Exception as e:
        st.error(f"Error loading O*NET data: {e}")
        return None

@st.cache_data
def load_bls_data():
    """Load BLS data files"""
    data_folder = "data/raw_data_project"
    bls_files = {
        'employment': 'Civilian_Employment_In_Thousands.csv',
        'unemployment': 'Unemployment_Rate.csv',
        'wage_analysts': 'Annual_mean_wage_for_Computer_and_Information_Analysts.csv',
        'hourly_wage': 'Hourly_mean_wage_for_Computer_and_Information_Analysts.csv',
        'projections': 'employment_projections_tech.csv'
    }
    
    bls_data = {}
    for key, filename in bls_files.items():
        filepath = os.path.join(data_folder, filename)
        if os.path.exists(filepath):
            try:
                bls_data[key] = pd.read_csv(filepath)
            except Exception as e:
                st.warning(f"Could not load {filename}: {e}")
    
    return bls_data

@st.cache_data
def load_job_listings_data():
    """Load job listings data from Google Sheets"""
    try:
        loader = JobDataLoader()
        df = loader.load_job_data(use_cache=True)
        if not df.empty:
            return loader.process_job_data(df)
        return pd.DataFrame()
    except Exception as e:
        st.warning(f"Could not load job listings data: {e}")
        return pd.DataFrame()

def clean_salary_data(salary_str):
    """Clean salary data"""
    if pd.isna(salary_str):
        return None
    
    salary_str = str(salary_str)
    
    if '$' in salary_str:
        salaries = re.findall(r'\$(\d+(?:\.\d{2})?)', salary_str)
        if salaries:
            return float(salaries[0])
    
    try:
        return float(salary_str)
    except:
        return None
