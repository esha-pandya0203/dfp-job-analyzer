#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
US Employment Data Analysis Dashboard
====================================

A comprehensive Streamlit dashboard for analyzing US employment data,
integrating O*NET data, BLS statistics, and job listings.

Author: Fan Yang (CMU)
Version: 2.0 (US Version)
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
from pages import overview, job_search

# Import utility modules
from utils.data_loader import load_pa_occupation_data, load_bls_data, clean_salary_data

# Import scraper manager
from modules.scrapers import ScraperManager

# Page configuration
st.set_page_config(
    page_title="US Employment Dashboard",
    page_icon="🇺🇸",
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

def check_data_updates():
    """Check for data updates using ScraperManager"""
    try:
        # Create scraper manager instance
        scraper_manager = ScraperManager()
        
        # Run smart update (only if needed)
        success = scraper_manager.run_smart_update()
        
        if success:
            st.success("✅ All data updated successfully!")
            return True
        else:
            st.info("ℹ️ All data is up to date")
            return False
            
    except Exception as e:
        st.warning(f"⚠️ Data update check failed: {str(e)}")
        return False

def run_full_scraping():
    """Run full data scraping process"""
    try:
        # Create scraper manager instance
        scraper_manager = ScraperManager()
        
        # Run comprehensive scraping
        results = scraper_manager.scrape_all_data()
        
        success_count = sum(results.values())
        if success_count > 0:
            st.success(f"✅ Scraping completed! {success_count}/3 operations successful.")
            return True
        else:
            st.error("❌ All scraping operations failed.")
            return False
            
    except Exception as e:
        st.error(f"❌ Scraping failed: {str(e)}")
        return False

def main():
    """Main Streamlit application"""
    
    # Sidebar
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.selectbox(
        "Choose Analysis Section",
        ["Overview", "Job Search"]
    )
    
    # Header
    if page == "Overview":
        st.markdown('<h1 class="main-header">US Employment Dashboard</h1>', unsafe_allow_html=True)
    elif page == "Job Search":
        st.markdown('<h1 class="main-header">US Job Search & Analysis</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Data management section
    with st.expander("🔄 Data Management", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Check for Updates"):
                with st.spinner("Checking for data updates..."):
                    check_data_updates()
        
        with col2:
            if st.button("🚀 Run Full Scraping"):
                with st.spinner("Running comprehensive data scraping..."):
                    if run_full_scraping():
                        st.rerun()  # Refresh the app to show new data
    
    # Load data
    with st.spinner("Loading data..."):
        job_data = load_pa_occupation_data()  # This now loads job data
        bls_data = load_bls_data()
    
    if job_data is None:
        st.error("Unable to load job data.")
        st.info("💡 Use the '🚀 Run Full Scraping' button above to collect fresh data.")
        st.stop()
    
    # Main content based on selected page
    if page == "Overview":
        overview.show_overview(job_data, bls_data)
    elif page == "Job Search":
        job_search.show_job_search()

if __name__ == "__main__":
    main()
