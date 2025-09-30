import streamlit as st 
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns 
from modules.nav import navbar 

st.set_page_config(page_title='Job Market Dashboard', page_icon='📊', layout='wide')
st.title('Job Analyzer') 
st.write('Explore salary trends, skills demand, and real job postings across North America.')

from pages import dashboard, job_search

def main(): 
    #webscrape all the data only the relevants ones reference bls_data dict 
    #store csv files in data/raw_data

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