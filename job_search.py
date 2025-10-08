import streamlit as st
import pandas as pd
from utils.job_title_mapping import find_soc_code 
from utils.data_loader import load_bls_data, load_prcoessed_job_data 

BLS_DATA = load_bls_data() 

def show_job_search(pa_wage_data):
    """Main job search page"""
    st.header("🔍 Job Search & Analysis")
    st.markdown("Search for specific job titles and get comprehensive market analysis")
    
    # search Interface
    st.subheader("📋 Search Interface")

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
        "onet_matches": [],
        "bls_data": None,
        "market_analysis": {}, 
        "job_data": None 
    }
    
    # find SOC code
    soc_info = find_soc_code(job_title)
    results["soc_info"] = soc_info
    
    if soc_info:
        job_data = load_prcoessed_job_data(soc_info['soc_code'])
        results["job_data"] = job_data
        
        # get BLS data if available
        if BLS_DATA is not None:
            bls_match = search_bls_data(soc_info["soc_code"])
            results["bls_data"] = bls_match
        
    return results

def search_bls_data(soc_code):
    """Search BLS data for SOC code"""
    if BLS_DATA is None:
        return None
    
    # this would search BLS data for the specific SOC code
    # TODO!! 
    return {
        "soc_code": soc_code,
        "employment_count": "N/A",
        "median_wage": "N/A",
        "employment_growth": "N/A"
    }

def display_search_results(search_results, search_input, pa_wage_data):
    """Display search results"""
    st.subheader(f"📃 Search Results for: '{search_input}'")
    
    job_listings = search_results["job_data"]
    st.subheader("💼 Available Job Listings")
    
    if job_listings is None or job_listings.empty:
        st.info("No job listings found for this position.")
        return
    
    st.write(f"Found {len(job_listings)} job listings:")
    st.write(f"Displaying 5 Jobs Per Category")
    
    # Check if job_category column exists, if not create a default one
    if 'job_category' not in job_listings.columns:
        if 'category' in job_listings.columns:
            job_listings['job_category'] = job_listings['category']
        else:
            job_listings['job_category'] = 'General'
    
    # Check if matched_skills column exists, if not create a default one
    if 'matched_skills' not in job_listings.columns:
        job_listings['matched_skills'] = [[]] * len(job_listings)
    
    grouped_data = job_listings.groupby('job_category')

    for category, group_df in grouped_data: 
        st.subheader(f"📁 {category} Jobs")

        top_5_jobs = group_df.head(5) 
    
        for i, job in top_5_jobs.iterrows():
            with st.expander(f"{i}. {job['title']} at {job['company']}"): #(Match Score: {job['match_score']})
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Company:** {job['company']}")
                    st.write(f"**Location:** {job['location']}")
                    st.write(f"**Average Salary:** ${job['avg_salary']}")
                    
                    if 'experience_level' in job and not pd.isna(job['experience_level']):
                        st.write(f"**Experience Level:** {job['experience_level']}")

                    if 'matched_skills' in job and job['matched_skills'] and len(job['matched_skills']) > 0:
                        # st.write("**Required Skills:**")
                        skills_text = ", ".join(job['matched_skills'][:5])  # Show first 5 skills
                        # skills_text = job['matched_skills'][:5]
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
                            # st.write(skills_text)
                            st.markdown(f"**Required Skills:** {skills_text}")
                
                with col2:
                    # Apply button
                    if job['redirect_url']:
                        st.markdown(f"[🔗 Apply Now]({job['redirect_url']})")
                    # elif job['redirect_link']:
                    #     st.markdown(f"[🔗 View Job]({job['redirect_link']})")
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