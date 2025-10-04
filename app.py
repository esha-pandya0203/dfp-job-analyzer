import streamlit as st 
import asyncio 
import sys 
from modules.nav import navbar 
from pages import dashboard, job_search

st.set_page_config(page_title='Job Market Dashboard', page_icon='📊', layout='wide')
st.title('Job Analyzer') 
st.write('Explore salary trends, skills demand, and real job postings across North America.')

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy()) 

from utils.data_scraper import collect_all_job_postings, clear_processed_data

def main(): 
    #webscrape all the data only the relevants ones reference bls_data dict 
    #store csv files in data/raw_data
    with st.spinner("⏳ Collecting job postings. This may take up to 10 minutes. Please be patient..."):
        clear_processed_data() 
        collect_all_job_postings() 

    #populate application dashboards 

    #navbar (need to add Overview and Job Search)
    navbar(); 
    page = st.sidebar.selectbox(
        "Choose Analysis Section",
        ["Dashboard", "Job Search"]
    )

     # Load data
    # with st.spinner("Loading data..."):
    #     # pa_data = load_pa_occupation_data()
    #     bls_data = load_bls_data()

    # if page == "Overview":
    #     overview.show_overview()
    # elif page == "Job Search":
    #     job_search.show_job_search()
    


if __name__ == "__main__":
    main()