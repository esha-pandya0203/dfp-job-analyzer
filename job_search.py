"""
------------------------------------------------------------
File: job_search.py
Team: Orange Team
Members: 
    - Jiatong Li (jiatong4)
    - Esha Pandya (epandya)
    - Fan Yang (fy4)
    - Sumreen Fathima (sumreenf)

Description:
    Code for the job search tab of the application, displays job listings depending on 
    the user's search input 

Imports:
    - Imports from: streamlit, pandas, utils
    - Imported by: app.py
------------------------------------------------------------
"""

import streamlit as st
import pandas as pd
from utils.job_title_mapping import find_soc_code 
from utils.data_loader import load_prcoessed_job_data 

# main function that processes search and displays results 
def show_job_search(pa_wage_data):
    """Main job search page"""
    st.header("🔍 Job Search & Analysis")
    st.markdown("Search for specific job titles and get comprehensive market analysis")
    
    # search interface
    search_input = st.selectbox('Select a Job:', ['Computer Programmers', 'Software Developers', 'Software Quality Assurance Analysts and Testers', 'Data Scientists', 'Computer and Information Systems Managers', 'Computer Network Architects'])

    # search results 
    if search_input: 
        search_results = perform_job_search(search_input)
        display_search_results(search_results, search_input, pa_wage_data)
    
def perform_job_search(job_title): 
    """Perform job search and return results"""
    results = {
        "job_title": job_title,
        "soc_info": None,
        "job_data": None 
    }
    
    # find SOC code
    soc_info = find_soc_code(job_title)
    results["soc_info"] = soc_info
    
    if soc_info:
        job_data = load_prcoessed_job_data(soc_info['soc_code'])
        results["job_data"] = job_data
        
    return results

def display_search_results(search_results, search_input, pa_wage_data):
    """Display search results"""    
    job_listings = search_results["job_data"]
    st.subheader("💼 Available Job Listings")
    
    if job_listings is None or job_listings.empty:
        st.info("No job listings found for this position.")
        return
    
    st.write(f"Found {len(job_listings)} job listings")

    PAGE_SIZE = 5     
    grouped_data = job_listings.groupby('job_category')

    # display job listings grouped by job cateogry 
    for category, group_df in grouped_data: 
        st.subheader(f"📁 {category} Jobs")

        # pagination to view a small number of jobs at once 
        category_key=f"page_{category}"
        if category_key not in st.session_state: 
            st.session_state[category_key] = 0 
        
        page_number = st.session_state[category_key] 
        start_idx = page_number * PAGE_SIZE 
        end_idx = start_idx + PAGE_SIZE 
        page_df = group_df.iloc[start_idx:end_idx]

        st.write(f"Viewing page {page_number + 1} of {((len(group_df)-1)//PAGE_SIZE)+1}")
    
        for i, job in page_df.iterrows():
            with st.expander(f"{i}. {job['title']} at {job['company']}"): #(Match Score: {job['match_score']})
                col1, col2 = st.columns([2, 1])
                
                # display job listing information 
                with col1:
                    st.write(f"**Company:** {job['company']}")
                    st.write(f"**Location:** {job['location']}")
                    st.write(f"**Average Salary:** ${job['avg_salary']}")
                    
                    if 'experience_level' in job and not pd.isna(job['experience_level']):
                        st.write(f"**Experience Level:** {job['experience_level']}")

                    if 'matched_skills' in job and job['matched_skills'] and len(job['matched_skills']) > 0:
                        skills_text = ", ".join(job['matched_skills'][:5])  # Show first 5 skills
                        if len(job['matched_skills']) > 5:
                            skills_text += f" (+{len(job['matched_skills']) - 5} more)"
                            st.write(skills_text)
                            
                            # Use session state to manage expand state
                            expand_key = f"skills_expand_{i}_{hash(str(job['matched_skills']))}"
                            if st.button("📖 View All Skills", key=f"job_listing_{expand_key}"):
                                st.session_state[expand_key] = True
                            
                            # Show expanded content if state is True
                            if st.session_state.get(expand_key, False):
                                all_skills = job['matched_skills']
                                st.info(f"**All Required Skills:** {all_skills}")
                                if st.button("🔙 Back", key=f"back_job_listing_{expand_key}"):
                                    st.session_state[expand_key] = False
                                    st.rerun()
                        else:
                            st.markdown(f"**Required Skills:** {skills_text}")
                
                with col2:
                    # Apply button
                    if job['redirect_url']:
                        st.markdown(f"[🔗 Apply Now]({job['redirect_url']})")
                    else:
                        st.write("No apply link available")
                    
                    # Additional info
                    if job['soc_code']:
                        soc_value = job.get('soc_code')

                        # Filter the DataFrame for the SOC code
                        match = pa_wage_data.loc[pa_wage_data['soc'] == soc_value, 'average_annual_wage']

                        if not match.empty and pd.notna(match.iloc[0]):
                            avg_wage = match.iloc[0]
                            st.write(f"**📊 Pittsburgh Wage Comparison Avg Annual Wage:** ${avg_wage:,.0f}")
                        else:
                            st.write("**📊 Pittsburgh Wage Comparison Avg Annual Wage:** N/A")

        # pagination buttons 
        col1, col2 = st.columns([1, 1])
        with col1: 
            if st.button("⬅️ Previous", key=f"prev_{category}"):
                if st.session_state[category_key] > 0: 
                    st.session_state[category_key] -= 1 
                    st.rerun() 

        with col2: 
            if st.button("➡️ Next", key=f'next_{category}'): 
                if end_idx < len(group_df):
                    st.session_state[category_key] += 1 
                    st.rerun()