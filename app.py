import streamlit as st 
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns 
from modules.nav import navbar 
from utils.bls_data_scraper import fetch_bls_data, web_scrape_bls_employment_projections, pittsburgh_computer_wage_outlook
from utils.data_loader import load_bls_data, load_pittsburgh_data
from data.bls_dict import bls_dict

st.set_page_config(page_title='Job Market Dashboard', page_icon='📊', layout='wide')
st.title('Job Analyzer') 
st.write('Explore salary trends, skills demand, and real job postings across North America.')

from pages import dashboard

def main(): 
    #webscrape all the data only the relevants ones reference bls_data dict 
    #store csv files in data/raw_data

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
        pa_wage_data = load_pittsburgh_data(bls_dict=bls_dict)
        print(pa_wage_data)
        bls_data = load_bls_data()

    if page == "Dashboard":
        dashboard.show_overview(bls_data)
    # elif page == "Job Search":
    #     job_search.show_job_search()
    


if __name__ == "__main__":
    main()