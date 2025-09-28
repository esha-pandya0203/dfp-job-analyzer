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

@st.cache_data
def load_pa_occupation_data():
    """Load Pennsylvania occupation data"""
    try:
        data_folder = "data/raw_data_project"
        pa_file = os.path.join(data_folder, "pennsylvania_all_occupations_20250927_201529.csv")
        
        if os.path.exists(pa_file):
            df = pd.read_csv(pa_file)
            return df
        else:
            st.error(f"File not found: {pa_file}")
            return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
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
