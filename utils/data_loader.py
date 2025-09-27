import pandas as pd 
import json 
import streamlit as st 

@st.cache_data
def load_prcoessed_job_data(category): 
    return pd.read_csv(f'data/processed_data/{category}')

@st.cache_data 
def load_general_stats(file_name):
    return pd.read_csv(f'data/processed_data/{file_name}')

@st.cache_data
def load_bls_mapping():
    with open('data/bls_dict.py', 'r') as f: 
        return json.load(f) 