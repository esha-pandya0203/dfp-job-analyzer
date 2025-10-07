import streamlit as st 
import asyncio 
import sys 
from modules.nav import navbar 
from utils.bls_data_scraper import fetch_bls_data, web_scrape_bls_employment_projections, pittsburgh_computer_wage_outlook
from utils.data_loader import load_bls_data, load_pittsburgh_data, load_job_data
from utils.data_scraper import collect_all_job_postings, clear_processed_data
from data.bls_dict import bls_dict
from pages import dashboard, job_search

st.set_page_config(page_title='Job Market Dashboard', page_icon='📊', layout='wide')
st.title('Job Analyzer') 
st.write('Explore salary trends, skills demand, and real job postings across North America.')

def main(): 

    navbar(); 
    page = st.sidebar.selectbox(
        "Choose Analysis Section",
        ["Dashboard", "Job Search"], 
        index = 0
    )

    #webscrape all the data only the relevants ones reference bls_data dict 
    #store csv files in data/raw_data
    # scrape all data on start-up, only occurs once per session 
    if 'startup_done' not in st.session_state:
        st.session_state.startup_done = True
        with st.spinner("⏳ Collecting data. This may take up to 10 minutes. Please be patient..."):
            clear_processed_data() 
            collect_all_job_postings() 

            fetch_bls_data()
            web_scrape_bls_employment_projections()
            pittsburgh_computer_wage_outlook()

    
    job_data = load_job_data()
    # TODO: remove if we are not using anywhere - it only comes up in this file when I search for it 
    pa_wage_data = load_pittsburgh_data(bls_dict=bls_dict) 
    print("pa wages for comparison" , pa_wage_data)
    bls_data = load_bls_data()

    # set up navigation 
    if page == "Dashboard":
        dashboard.show_overview(job_data, bls_data)
    elif page == "Job Search":
        job_search.show_job_search(pa_wage_data); 
    
if __name__ == "__main__":
    main()