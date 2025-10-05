import streamlit as st 
import asyncio 
import sys 
from modules.nav import navbar 
from utils.bls_data_scraper import fetch_bls_data, web_scrape_bls_employment_projections, pittsburgh_computer_wage_outlook
from utils.data_loader import load_bls_data, load_pittsburgh_data, load_job_data
from utils.data_scraper import collect_all_job_postings, clear_processed_data
from data.bls_dict import bls_dict

st.set_page_config(page_title='Job Market Dashboard', page_icon='📊', layout='wide')
st.title('Job Analyzer') 
st.write('Explore salary trends, skills demand, and real job postings across North America.')

from pages import dashboard

def main(): 
    #webscrape all the data only the relevants ones reference bls_data dict 
    #store csv files in data/raw_data
    # with st.spinner("⏳ Collecting job postings. This may take up to 10 minutes. Please be patient..."):
    #     clear_processed_data() 
    #     collect_all_job_postings() 

    #BLS DATA SCRAPE/API REQUESTS 
    fetch_bls_data()
    web_scrape_bls_employment_projections()
    pittsburgh_computer_wage_outlook()


    #navbar (need to add Overview and Job Search)
    # navbar(); 
    page = st.sidebar.selectbox(
        "Choose Analysis Section",
        ["Dashboard", "Job Search"]
    )

     # Load data
    with st.spinner("Loading data..."):
        job_data = load_job_data()
        pa_wage_data = load_pittsburgh_data(bls_dict=bls_dict)
        print(pa_wage_data)
        bls_data = load_bls_data()

    if page == "Dashboard":
        dashboard.show_overview(job_data, bls_data, bls_dict)
    # elif page == "Job Search":
    #     job_search.show_job_search()
    


if __name__ == "__main__":
    main()