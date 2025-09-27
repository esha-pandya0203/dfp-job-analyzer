import streamlit as st 
import pandas as pd 
from modules.nav import navbar

st.title("🔎 Job Role Insights")
navbar() 

# load data 

# load mapping of jobs to categories 

# search for a job title 
name = st.text_input('Search for a job:')
if st.button('Search'):
    result = name.title()
    st.success(result)

job = st.selectbox('Select a Job:', ['AI/ML', 'Cloud Engineer', 'IT', 'Software Developer', 'DevOps', 'Operations', 'QA', 'Data Analyst', 'Data Scientist', 'Data Engineer', 'Technical Product Manager', 'Cybersecurity'])
st.write('Your job is:', job)

# filter jobs and return stats about specific job 

# pull stats from national statistics 

# metrics 
st.metric('Total Postings', 500) # replace with len(result of filtering jobs) 
st.metric('Average Salary', 0) # replace with f"${filtered['Salary_min'].mean():,.0f} - ${filtered['Salary_max'].mean():,.0f}" 

# skills chart 
st.subheader("🧩 Top Skills in Job Descriptions")
# skill_fig = (filter skills based on job searched)
# st.pyplot(skill_fig)

# job postings 
