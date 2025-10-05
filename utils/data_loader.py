import pandas as pd 
import json 
import streamlit as st 
import os
import re


@st.cache_data
def load_prcoessed_job_data(category): 
    return pd.read_csv(f'data/processed_data/{category}')

@st.cache_data 
def load_general_stats(file_name):
    return pd.read_csv(f'data/processed_data/{file_name}')

@st.cache_data
def load_bls_data():
    """Load BLS data files"""
    data_folder = "data/raw_data"
    bls_files = {
        'employment_level': 'LNS12000000.csv',
        'unemployment_level': 'LNS13000000.csv',
        'projections': 'employment_projections_tech.csv',
        'hourly_wage_all': 'CES0500000003.csv'
    }
    
    bls_data = {}
    for key, filename in bls_files.items():
        filepath = os.path.join(data_folder, filename)
        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath)
                df.columns = df.columns.str.strip()
                
                if 'Value' in df.columns:
                    # Time-series datasets (have Date)
                    df = df.rename(columns={'Value': key})
                    if 'Date' in df.columns:
                        df['Date'] = pd.to_datetime(df['Date'])
                else:
                    # Non-time-series dataset (like projections)
                    st.info(f"Loaded {filename} (non-time-series dataset)")

                bls_data[key] = df

            except Exception as e:
                st.warning(f"Could not load {filename}: {e}")
        else:
            st.warning(f"File not found: {filename}")

    return bls_data


@st.cache_data
def load_pittsburgh_data(bls_dict, wage_filename="pittsburgh_computer_wage_outlook.csv", 
                            outlook_filename="pittsburgh_computer_occupation_outlook.csv"):
    """Load and clean BLS wage data and map SOC codes to keyword categories"""
    data_folder = "data/raw_data"
    wage_filepath = os.path.join(data_folder, wage_filename)
    outlook_filepath = os.path.join(data_folder, outlook_filename)
    
    if not os.path.exists(wage_filepath):
        st.warning(f"⚠️ File not found: {wage_filepath}")
        return pd.DataFrame()
    
    try:
        wage_rows = []
    
        with open(wage_filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("Average"):  # skip header lines
                    continue
                line = line.strip('"')
                
                # Extract numeric values from the line
                wages = re.findall(r'[\d,]+(?:\.\d+)?', line)
                if len(wages) < 3:
                    continue  # skip incomplete lines
                
                # Last 3 numeric fields are the ones we care about
                median_annual = float(wages[-5].replace(',', ''))
                avg_annual = float(wages[-6].replace(',', ''))
                avg_hourly = float(wages[-7].replace(',', ''))
                
                # SOC code is the first field
                soc = line.split()[0]

                if soc not in bls_dict:
                    continue
                
                # Title is everything between SOC and numeric wages
                title = line[len(soc):].strip()  # remove SOC
                # Remove wage numbers from title
                for w in wages:
                    title = title.replace(w, '')
                title = re.sub(r'\s+', ' ', title).strip()  # clean extra spaces
                
                wage_rows.append([soc, title, avg_hourly, avg_annual, median_annual])
        
        df_wages = pd.DataFrame(wage_rows, columns=['soc', 'title', 'average_hourly_wage', 'average_annual_wage', 'median_annual_wage'])
        
        return df_wages

    except Exception as e:
        st.error(f"❌ Error loading wage data: {e}")
        return pd.DataFrame()
    
@st.cache_data
def load_job_data():
    """Load job data from scraper"""
    try:
        # Try to load job data from various sources
        data_files = [
            # "data/raw_data/15-1251.csv",
            # "data/raw_data/15-1252.csv", 
            # "data/raw_data/15-1253.csv",
            "data/raw_data/15-2050.csv",
            # "data/raw_data/11-3021.csv",
            # "data/raw_data/15-1241.csv"
        ]
        
        for file_path in data_files:
            print(file_path)
            if os.path.exists(file_path):
                print("found file")
                df = pd.read_csv(file_path)
                print("uncleaned", df.head())
                if not df.empty:
                    # Clean and standardize the data
                    df = clean_job_data(df)
                    print("cleaned", df.head())
                    return df
        
        # If no data exists, create some mock data for demo
        st.warning("No job data found. Creating mock data for demo...")
        mock_data = create_mock_job_data()
        return mock_data
        
    except Exception as e:
        st.error(f"Error loading job data: {e}")
        return None
def create_mock_job_data():
    """Create mock job data for demonstration"""
    import pandas as pd
    
    mock_jobs = [
        {
            'title': 'Software Engineer',
            'code': '15-1252',
            'description': 'Develops, creates, and modifies general computer applications software or specialized utility programs.',
            'skills': ['Python', 'JavaScript', 'SQL', 'Git'],
            'education': 'Bachelor\'s degree in Computer Science or related field',
            'salary': '$85,000 - $120,000',
            'employment': 'High demand'
        },
        {
            'title': 'Data Scientist',
            'code': '15-2050',
            'description': 'Extracts insights from data using statistical analysis and machine learning techniques.',
            'skills': ['Python', 'R', 'Machine Learning', 'Statistics'],
            'education': 'Master\'s degree in Data Science or related field',
            'salary': '$90,000 - $130,000',
            'employment': 'Growing rapidly'
        },
        {
            'title': 'Data Analyst',
            'code': '15-2050',
            'description': 'Analyzes data to help organizations make informed business decisions.',
            'skills': ['Excel', 'SQL', 'Tableau', 'Python'],
            'education': 'Bachelor\'s degree in Business or related field',
            'salary': '$55,000 - $80,000',
            'employment': 'Steady demand'
        },
        {
            'title': 'Product Manager',
            'code': '11-3021',
            'description': 'Oversees product development and manages product lifecycle.',
            'skills': ['Project Management', 'Analytics', 'Communication', 'Strategy'],
            'education': 'Bachelor\'s degree in Business or related field',
            'salary': '$75,000 - $110,000',
            'employment': 'High demand'
        },
        {
            'title': 'UX Designer',
            'code': '27-1024',
            'description': 'Designs user experiences for digital products and services.',
            'skills': ['Figma', 'User Research', 'Prototyping', 'Design Thinking'],
            'education': 'Bachelor\'s degree in Design or related field',
            'salary': '$65,000 - $95,000',
            'employment': 'Growing field'
        }
    ]
    
    return pd.DataFrame(mock_jobs)

def clean_job_data(df):
    """Clean and standardize job data"""
    # Create a copy to avoid modifying original
    df_clean = df.copy()
    
    # Standardize column names
    column_mapping = {
        'title': 'title',
        'companyName': 'company',
        'description': 'description', 
        'location': 'location',
        'avg_salary': 'avg_salary',
        'experienceLevel': 'experience_level',
        'skills': 'skills',
        'Job_Category_Code': 'soc_code'
    }
    #title,company,location,category,avg_salary,description,redirect_url,experience_level,soc_code
    
    # Rename columns if they exist
    for old_name, new_name in column_mapping.items():
        if old_name in df_clean.columns:
            df_clean[new_name] = df_clean[old_name]
    
    # Ensure required columns exist
    required_columns = ['title', 'description', 'soc_code']
    for col in required_columns:
        if col not in df_clean.columns:
            if col == 'soc_code':
                df_clean[col] = '15-1251'  # Default SOC code
            else:
                df_clean[col] = 'N/A'
    
    # # Clean skills column - convert string representation of list to actual list
    if 'skills' in df_clean.columns:
        def parse_skills(skills_str):
            if pd.isna(skills_str) or skills_str == 'N/A':
                return []
            if isinstance(skills_str, str):
                try:
                    # Handle string representation of list
                    import ast
                    return ast.literal_eval(skills_str)
                except:
                    # If parsing fails, split by comma
                    return [s.strip().strip("'\"") for s in skills_str.split(',')]
            return skills_str if isinstance(skills_str, list) else []
        
        df_clean['skills'] = df_clean['skills'].apply(parse_skills)
    
    # Add salary column if not exists
    # if 'salary' not in df_clean.columns:
    #     if 'salary_min' in df_clean.columns and 'salary_max' in df_clean.columns:
    #         df_clean['salary'] = df_clean.apply(
    #             lambda row: f"${row['salary_min']} - ${row['salary_max']}" 
    #             if pd.notna(row['salary_min']) and pd.notna(row['salary_max']) 
    #             else 'Not Specified', axis=1
    #         )
    #     else:
    #         df_clean['salary'] = 'Not Specified'
    
    # # Add education column if not exists
    # if 'education' not in df_clean.columns:
    #     df_clean['education'] = 'Not Specified'
    
    return df_clean

@st.cache_data
def load_pa_occupation_data():
    """Load occupation data (alias for load_job_data)"""
    return load_job_data()