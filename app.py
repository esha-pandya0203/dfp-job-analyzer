import streamlit as st 
from utils.bls_data_scraper import fetch_bls_data, web_scrape_bls_employment_projections, pittsburgh_computer_wage_outlook
from utils.data_loader import load_bls_data, load_pittsburgh_data, load_job_data
from utils.data_scraper import collect_all_job_postings, clear_processed_data
from utils.onet_scraper import EnhancedONETScraper
from data.bls_dict import bls_dict
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
        with st.spinner("⏳ Collecting data. This may take up to 10 minutes. Please be patient..."):
            #clear_processed_data() 
            #collect_all_job_postings() 
            try:
                with open('data/api-bls.csv', 'r', newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    row = next(reader)  # Get the first and only row
                    api_key = row[1]
            except FileNotFoundError:
                print("Error: 'api-bls.csv' not found.")
            fetch_bls_data(api_key)
            web_scrape_bls_employment_projections()
            pittsburgh_computer_wage_outlook()
            
            # Collect O*NET data - use incremental update
            scraper = EnhancedONETScraper()
            scraper.run_incremental_update()
            scraper.cleanup_temp_files()

    
    job_data = load_job_data()
    pa_wage_data = load_pittsburgh_data(bls_dict=bls_dict) 
    bls_data = load_bls_data()
    
    # Load O*NET data - prioritize the larger dataset
    onet_data = None
    nested_csv = 'dfp-job-analyzer/data/ONET_Data.csv'
    root_csv = 'data/ONET_Data.csv'
    
    if os.path.exists(nested_csv):
        onet_data = pd.read_csv(nested_csv)
        print(f"✅ Loaded O*NET data from nested directory: {len(onet_data)} occupations")
    elif os.path.exists(root_csv):
        onet_data = pd.read_csv(root_csv)
        print(f"✅ Loaded O*NET data from root directory: {len(onet_data)} occupations")

    # set up navigation 
    if page == "Dashboard":
        dashboard.show_overview(job_data, bls_data, onet_data)
    elif page == "Job Search":
        job_search.show_job_search(pa_wage_data); 
    
if __name__ == "__main__":
    main()