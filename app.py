#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pennsylvania Employment Data Analysis Dashboard
==============================================

A comprehensive Streamlit dashboard for analyzing Pennsylvania employment data,
integrating O*NET data, BLS statistics, and job listings from Google Sheets.

Author: Fan Yang (CMU)
Version: 2.0 (Refactored)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import re
from collections import Counter
import requests
from datetime import datetime
import json

# Import page modules
from pages import overview, occupation_analysis, skills_analysis, salary_analysis, bls_statistics, data_integration, job_search

# Import utility modules
from utils.data_loader import load_pa_occupation_data, load_bls_data, clean_salary_data

# Page configuration
st.set_page_config(
    page_title="Pennsylvania Employment Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🏛️ Pennsylvania Employment Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.selectbox(
        "Choose Analysis Section",
        ["Overview", "Job Search", "Occupation Analysis", "Skills Analysis", "Salary Analysis", "BLS Statistics", "Data Integration"]
    )
    
    # Load data
    with st.spinner("Loading data..."):
        pa_data = load_pa_occupation_data()
        bls_data = load_bls_data()
    
    if pa_data is None:
        st.error("Unable to load Pennsylvania occupation data. Please check file paths.")
        return
    
    # Clean salary data
    if 'salary_median' in pa_data.columns:
        pa_data['salary_median_clean'] = pa_data['salary_median'].apply(clean_salary_data)
    
    # Main content based on selected page
    if page == "Overview":
        overview.show_overview(pa_data, bls_data)
    elif page == "Job Search":
        job_search.show_job_search()
    elif page == "Occupation Analysis":
        occupation_analysis.show_occupation_analysis(pa_data)
    elif page == "Skills Analysis":
        skills_analysis.show_skills_analysis(pa_data)
    elif page == "Salary Analysis":
        salary_analysis.show_salary_analysis(pa_data)
    elif page == "BLS Statistics":
        bls_statistics.show_bls_statistics(bls_data)
    elif page == "Data Integration":
        data_integration.show_data_integration(pa_data, bls_data)

if __name__ == "__main__":
    main()
