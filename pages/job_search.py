import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.job_title_mapping import match_job_title_to_soc_code, find_soc_code, get_all_job_titles, get_categories
from utils.data_loader import load_job_data, load_bls_data, load_prcoessed_job_data

# JOB_DATA = load_job_data() 
BLS_DATA = load_bls_data() 

def show_job_search():
    """Main job search page"""
    st.header("🔍 Job Search & Analysis")
    st.markdown("Search for specific job titles and get comprehensive market analysis")
    
    # search Interface
    st.subheader("📋 Search Interface")

    search_input = st.selectbox('Select a Job:', ['Computer Programmers', 'Software Developers', 'Software Quality Assurance Analysts and Testers', 'Data Scientists', 'Computer and Information Systems Managers', 'Computer Network Architects'])

    # search results 
    if search_input: 
        search_results = perform_job_search(search_input)
        display_search_results(search_results, search_input)
    
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
        
        # Perform market analysis
#         results["market_analysis"] = analyze_job_market(onet_matches, bls_data, job_listings)
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

# def analyze_job_market(onet_matches, bls_data, job_listings):
#     """Analyze job market based on available data"""
#     analysis = {
#         "salary_range": "N/A",
#         "skill_requirements": [],
#         "education_requirements": "N/A",
#         "market_demand": "N/A",
#         "growth_projection": "N/A"
#     }
    
#     if onet_matches:
#         # Analyze salary data
#         salaries = []
#         for match in onet_matches:
#             if match.get('salary_median') and str(match['salary_median']) != 'nan':
#                 try:
#                     salary = float(str(match['salary_median']).replace('$', '').replace(',', ''))
#                     salaries.append(salary)
#                 except:
#                     pass
        
#         if salaries:
#             analysis["salary_range"] = f"${min(salaries):,.0f} - ${max(salaries):,.0f}"
        
#         # Analyze skills
#         all_skills = []
#         for match in onet_matches:
#             skills = match.get('technology_skills', '')
#             if skills and str(skills) != 'nan':
#                 # Parse skills string
#                 skills_list = str(skills).strip("[]").replace("'", "").split(", ")
#                 all_skills.extend([s.strip() for s in skills_list if s.strip()])
        
#         # Get most common skills
#         if all_skills:
#             skill_counts = pd.Series(all_skills).value_counts()
#             analysis["skill_requirements"] = skill_counts.head(10).to_dict()
        
#         # Analyze education requirements
#         education_levels = [match.get('education_level', '') for match in onet_matches]
#         if education_levels:
#             analysis["education_requirements"] = max(set(education_levels), key=education_levels.count)
    
#     return analysis

def display_search_results(search_results, search_input):
    """Display search results"""
    st.subheader(f"🔍 Search Results for: '{search_input}'")
    
#     # SOC Code Information
#     if results["soc_info"]:
#         soc_info = results["soc_info"]
        
#         col1, col2, col3 = st.columns([1, 2, 1])
        
#         with col1:
#             st.metric(
#                 label="BLS SOC Code",
#                 value=soc_info["soc_code"],
#                 delta=soc_info["soc_title"]
#             )
        
#         with col2:
#             # Use expandable display for category
#             if len(str(soc_info["category"])) > 25:
#                 truncated = str(soc_info["category"])[:22] + "..."
#                 st.metric(
#                     label="Category",
#                     value=truncated,
#                     delta="Job Family"
#                 )
#                 if st.button("📖 View Full Category", key=f"category_expand_{hash(soc_info['category'])}"):
#                     st.info(f"**Full Category:** {soc_info['category']}")
#             else:
#                 st.metric(
#                     label="Category",
#                     value=soc_info["category"],
#                     delta="Job Family"
#                 )
        
#         with col3:
#             st.metric(
#                 label="O*NET Matches",
#                 value=len(results["onet_matches"]),
#                 delta="Similar Occupations"
#             )
#     else:
#         st.warning(f"No BLS SOC code found for '{search_input}'. Try a different job title.")
#         return
    
#     # Market Analysis
#     if results["market_analysis"]:
#         display_market_analysis(results["market_analysis"])
    
#     # O*NET Matches
#     if results["onet_matches"]:
#         display_onet_matches(results["onet_matches"])
    
    # Job Listings
    display_job_listings(search_results["job_data"])
    
#     # BLS Data
#     if results["bls_data"]:
#         display_bls_data(results["bls_data"])

# def clean_education_text(education_text):
#     """Return education level text as-is without cleaning"""
#     if not education_text or education_text == "N/A":
#         return "N/A"
    
#     # Return the original text without any cleaning
#     return str(education_text)

# def display_expandable_text(label, text, max_length=30, key_prefix=""):
#     """Display text with expandable functionality if it's too long"""
#     if not text or text == "N/A":
#         st.metric(label=label, value="N/A")
#         return
    
#     text = str(text)
    
#     # If text is short enough, display normally
#     if len(text) <= max_length:
#         st.metric(label=label, value=text)
#     else:
#         # Display truncated version with expand option
#         truncated = text[:max_length-3] + "..."
#         st.metric(label=label, value=truncated)
        
#         # Add expand button
#         if st.button("📖 View Full Text", key=f"{key_prefix}_expand_{hash(text)}"):
#             st.info(f"**{label}:** {text}")

# def display_market_analysis(analysis):
#     """Display market analysis results"""
#     st.subheader("📊 Market Analysis")
    
#     col1, col2 = st.columns([1, 1])
    
#     with col1:
#         st.metric("Salary Range", analysis["salary_range"])
#         # Clean and display education level with expandable functionality
#         clean_education = clean_education_text(analysis["education_requirements"])
#         if len(clean_education) > 25:
#             truncated = clean_education[:22] + "..."
#             st.metric("Education Level", truncated)
            
#             # Use session state to manage expand state
#             expand_key = f"education_expand_{hash(clean_education)}"
#             if st.button("📖 View Full Education", key=f"market_analysis_{expand_key}"):
#                 st.session_state[expand_key] = True
            
#             # Show expanded content if state is True
#             if st.session_state.get(expand_key, False):
#                 st.info(f"**Full Education Level:** {clean_education}")
#                 if st.button("🔙 Back to Results", key=f"back_market_analysis_{expand_key}"):
#                     st.session_state[expand_key] = False
#                     st.rerun()
#         else:
#             st.metric("Education Level", clean_education)
    
#     with col2:
#         st.metric("Market Demand", analysis["market_demand"])
#         st.metric("Growth Projection", analysis["growth_projection"])
    
#     # Skills Analysis
#     if analysis["skill_requirements"]:
#         st.subheader("🛠️ Top Required Skills")
        
#         skills_df = pd.DataFrame([
#             {"Skill": skill, "Frequency": count}
#             for skill, count in analysis["skill_requirements"].items()
#         ])
        
#         fig = px.bar(
#             skills_df.head(10),
#             x="Frequency",
#             y="Skill",
#             orientation="h",
#             title="Most Frequently Required Skills",
#             color="Frequency",
#             color_continuous_scale="Blues"
#         )
#         fig.update_layout(height=400)
#         st.plotly_chart(fig, use_container_width=True)

def display_job_listings(job_listings):
    """Display job listings with apply buttons"""
    st.subheader("💼 Available Job Listings")
    
    if job_listings is None or job_listings.empty:
        st.info("No job listings found for this position.")
        return
    
    st.write(f"Found {len(job_listings)} job listings:")
    st.write(f"Displaying 5 Jobs Per Category")
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
                    st.write(f"**Average Salary:** {job['avg_salary']}")
                    
                    # if job['salary_min'] and job['salary_max']:
                    #     st.write(f"**Salary Range:** ${job['salary_min']:,.0f} - ${job['salary_max']:,.0f}")
                    # elif job['salary_min']:
                    #     st.write(f"**Min Salary:** ${job['salary_min']:,.0f}")
                    # elif job['salary_max']:
                    #     st.write(f"**Max Salary:** ${job['salary_max']:,.0f}")
                    
                    if job['experience_level']:
                        st.write(f"**Experience Level:** {job['experience_level']}")
                    
                    if job['matched_skills'] and len(job['matched_skills']) > 0:
                        st.write("**Required Skills:**")
                        #skills_text = ", ".join(job['matched_skills'][:5])  # Show first 5 skills
                        skills_text = job['matched_skills'][:5]
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
                            st.write(skills_text)
                
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
                        st.write(f"**SOC Code:** {job['soc_code']}")

# def display_bls_data(bls_data):
#     """Display BLS data"""
#     st.subheader("📈 BLS Labor Statistics")
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.metric("Employment Count", bls_data["employment_count"])
    
#     with col2:
#         st.metric("Median Wage", bls_data["median_wage"])
    
#     with col3:
#         st.metric("Employment Growth", bls_data["employment_growth"])

# def show_available_job_titles(selected_category):
#     """Show available job titles for browsing"""
#     st.subheader("📋 Available Job Titles")
    
#     all_titles = get_all_job_titles()
    
#     if selected_category != "All Categories":
#         # Filter by category
#         from utils.job_title_mapping import get_job_titles_by_category
#         all_titles = get_job_titles_by_category(selected_category)
    
#     # Display in columns
#     cols = st.columns(3)
#     titles_per_col = len(all_titles) // 3
    
#     for i, col in enumerate(cols):
#         start_idx = i * titles_per_col
#         end_idx = start_idx + titles_per_col if i < 2 else len(all_titles)
        
#         with col:
#             for idx, title in enumerate(all_titles[start_idx:end_idx]):
#                 # Use index to ensure unique keys
#                 if st.button(title, key=f"title_{i}_{idx}_{title}"):
#                     st.session_state.job_search_input = title
#                     st.rerun()
    
#     # Instructions
#     st.info("💡 **Tip:** Click on any job title above to search, or type your own in the search box above.")

# def show_job_listings_summary(job_listings):
#     """Show summary of available job listings"""
#     st.subheader("📋 Available Job Listings")
    
#     if job_listings.empty:
#         st.info("No job listings data available")
#         return
    
#     # Basic statistics
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.metric("Total Jobs", len(job_listings))
    
#     with col2:
#         unique_companies = job_listings['Company'].nunique() if 'Company' in job_listings.columns else 0
#         st.metric("Companies", unique_companies)
    
#     with col3:
#         if 'SOC_Code' in job_listings.columns:
#             unique_soc_codes = job_listings['SOC_Code'].nunique()
#             st.metric("Job Categories", unique_soc_codes)
#         else:
#             st.metric("Job Categories", "N/A")
    
#     with col4:
#         if 'Salary_min_clean' in job_listings.columns:
#             avg_salary = job_listings['Salary_min_clean'].mean()
#             st.metric("Avg Min Salary", f"${avg_salary:,.0f}" if not pd.isna(avg_salary) else "N/A")
#         else:
#             st.metric("Avg Min Salary", "N/A")
    
#     # Top companies
#     if 'Company' in job_listings.columns:
#         st.subheader("🏢 Top Companies")
#         company_counts = job_listings['Company'].value_counts().head(10)
        
#         fig = px.bar(
#             x=company_counts.values,
#             y=company_counts.index,
#             orientation='h',
#             title="Companies with Most Job Postings",
#             labels={'x': 'Number of Jobs', 'y': 'Company'}
#         )
#         fig.update_layout(height=400)
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Job categories
#     if 'SOC_Code' in job_listings.columns:
#         st.subheader("📊 Job Categories")
#         soc_counts = job_listings['SOC_Code'].value_counts()
        
#         fig = px.pie(
#             values=soc_counts.values,
#             names=soc_counts.index,
#             title="Distribution of Job Categories"
#         )
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Sample job listings with apply buttons
#     st.subheader("📝 Sample Job Listings")
    
#     # Show first 5 job listings with apply buttons
#     for idx, row in job_listings.head(5).iterrows():
#         with st.expander(f"{row.get('Job_title', 'N/A')} at {row.get('Company', 'N/A')}"):
#             col1, col2 = st.columns([2, 1])
            
#             with col1:
#                 st.write(f"**Company:** {row.get('Company', 'N/A')}")
#                 st.write(f"**Location:** {row.get('Location', 'N/A')}")
                
#                 if 'Salary_min_clean' in job_listings.columns and pd.notna(row.get('Salary_min_clean')):
#                     st.write(f"**Min Salary:** ${row.get('Salary_min_clean'):,.0f}")
#                 if 'Salary_max_clean' in job_listings.columns and pd.notna(row.get('Salary_max_clean')):
#                     st.write(f"**Max Salary:** ${row.get('Salary_max_clean'):,.0f}")
                
#                 if 'Experience_level' in job_listings.columns and pd.notna(row.get('Experience_level')):
#                     st.write(f"**Experience Level:** {row.get('Experience_level')}")
            
#             with col2:
#                 # Apply button
#                 apply_url = row.get('Apply_url', '') or row.get('apply_url', '') or row.get('ApplyURL', '')
#                 redirect_link = row.get('Redirect_link', '')
                
#                 if apply_url:
#                     st.markdown(f"[🔗 Apply Now]({apply_url})")
#                 elif redirect_link:
#                     st.markdown(f"[🔗 View Job]({redirect_link})")
#                 else:
#                     st.write("No apply link available")
    
#     # Show remaining listings in a table
#     if len(job_listings) > 5:
#         st.subheader("📋 All Job Listings")
#         display_columns = ['Job_title', 'Company', 'Location']
#         if 'Salary_min_clean' in job_listings.columns:
#             display_columns.append('Salary_min_clean')
#         if 'Experience_level' in job_listings.columns:
#             display_columns.append('Experience_level')
        
#         available_columns = [col for col in display_columns if col in job_listings.columns]
#         if available_columns:
#             st.dataframe(
#                 job_listings[available_columns],
#                 use_container_width=True
#             )

show_job_search()