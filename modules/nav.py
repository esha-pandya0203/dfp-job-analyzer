import streamlit as st 

def navbar():
    with st.sidebar:
        st.sidebar.title('Navigation')
        st.page_link('pages/dashboard.py', label='Dashboard', icon='📈')
        st.page_link('pages/job_search.py', label='Job Role Insights', icon='🔎')
