import pandas as pd 
import json 
import streamlit as st 
import os

@st.cache_data
def load_prcoessed_job_data(category): 
    return pd.read_csv(f'data/processed_data/{category}')

@st.cache_data 
def load_general_stats(file_name):
    return pd.read_csv(f'data/processed_data/{file_name}')

@st.cache_data
def load_bls_data():
    """Load BLS data files"""
    data_folder = "data/raw_data"
    bls_files = {
        'employment_level': 'LNS12000000.csv',
        'unemployment_level': 'LNS13000000.csv',
        'annual_wage_computer_analysts': 'OEUN000000051--5215121004.csv',
        'hourly_wage_computer_analysts': 'OEUN000000051--5215121003.csv',
        'projections': 'employment_projections_tech.csv',
        'hourly_wage_all': 'CES0500000003.csv'
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