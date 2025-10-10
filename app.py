"""
------------------------------------------------------------
File: app.py
Team: Orange Team
Members: 
    - Jiatong Li (jiatong4)
    - Esha Pandya (epandya)
    - Fan Yang (fy4)
    - Sumreen Fathima (sumreenf)

Description:
    Main file for the project, compiles the other functions to scrape, load, and display cleaned data 

Imports:
    - Imports from: utils and data folder, streamlit, pandas, os, csv 
    - Imported by: none
------------------------------------------------------------
"""

import streamlit as st 
from utils.bls_data_scraper import fetch_bls_data, web_scrape_bls_employment_projections, pittsburgh_computer_wage_outlook
from utils.data_loader import load_bls_data, load_pittsburgh_data, load_job_data
from utils.data_scraper import collect_all_job_postings, clear_processed_data
from utils.onet_scraper import EnhancedONETScraper
import dashboard, job_search
import csv
import pandas as pd
import os

st.set_page_config(page_title='Job Market Dashboard', page_icon='📊', layout='wide')
st.title('Job Analyzer') 
st.write('Explore salary trends, skills demand, and real job postings across North America.')

def main(): 
    page = st.sidebar.selectbox(
        "Choose Analysis Section",
        ["Dashboard", "Job Search"], 
        index = 0
    )

    # scrape all data on start-up, only occurs once per session 
    if 'startup_done' not in st.session_state:
        st.session_state.startup_done = True
        st.info("Would you like to use previously scraped data or download new job data?")
        user_choice = st.radio(
            "Choose data source:", 
            ("Use cached data (faster)", "Download new data (takes up to 15 minutes)")
        )

        if user_choice == 'Download new data (takes up to 10 minutes)':
            with st.spinner("⏳ Collecting data. This may take up to 10 minutes. Please be patient..."):
                clear_processed_data() 
                collect_all_job_postings() 
                try:
                    with open('data/api-bls.csv', 'r', newline='') as csvfile:
                        reader = csv.reader(csvfile)
                        row = next(reader)  # Get the API KEY for bls 
                        api_key = row[1]
                except FileNotFoundError:
                    print("Error: 'api-bls.csv' not found.")

                # make API requests to BLS api endpoint and scrape BLS webpage for data
                fetch_bls_data(api_key)
                web_scrape_bls_employment_projections()
                # scrape pdf for pittsburgh specific outlook data
                pittsburgh_computer_wage_outlook()
                
                # collect O*NET data - use incremental update
                scraper = EnhancedONETScraper()
                scraper.run_incremental_update()
                scraper.cleanup_temp_files()

    # load all the data: job listings, pittsburgh wage and bls data
    job_data = load_job_data()
    pa_wage_data = load_pittsburgh_data() 
    bls_data = load_bls_data()
    
    # load O*NET data - prioritize the larger dataset
    onet_data = None
    root_csv = 'data/ONET_Data.csv'
    
    if os.path.exists(root_csv):
        onet_data = pd.read_csv(root_csv)
        print(f"✅ Loaded O*NET data from root directory: {len(onet_data)} occupations")

    # set up navigation on application interface
    if page == "Dashboard":
        dashboard.show_overview(job_data, bls_data, onet_data)
    elif page == "Job Search":
        job_search.show_job_search(pa_wage_data); 
    
if __name__ == "__main__":
    main()