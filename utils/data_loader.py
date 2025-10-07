import pandas as pd 
import json 
import streamlit as st 
import os
import re

@st.cache_data
def load_prcoessed_job_data(soc_code): 
    filepath = f'data/processed_data/{soc_code}.csv'
    if os.path.exists(filepath):
        return pd.read_csv(filepath)

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
                    print(f"Loaded {filename} (non-time-series dataset)")

                bls_data[key] = df

            except Exception as e:
                print(f"Could not load {filename}: {e}")
        else:
            print(f"File not found: {filename}")

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
    # get csv files from processed_data folder 
    filepath = 'data/processed_data'
    data_files = [
        os.path.join(filepath, file) for file in os.listdir(filepath) if file.endswith('.csv')
    ]

    try:
        column_names = ["title", "company", "location", "avg_salary", "description", "redirect_url", "experience_level", "soc_code", "job_category", "matched_skills"]
        concat_rows = pd.DataFrame(columns=column_names)
        
        for file_path in data_files:
            print(file_path)
            if os.path.exists(file_path):
                print("found file")
                df = pd.read_csv(file_path)
                if not df.empty:
                    # Clean and standardize the data
                    df = clean_job_data(df)
                    # print("cleaned", df.head())
                    concat_rows = pd.concat([concat_rows, df])
                
        return concat_rows
        
    except Exception as e:
        st.error(f"Error loading job data: {e}")
        return None

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
        'Matched_Skills': 'matched_skills',
        'Job_Category_Code': 'soc_code',
        'category': 'job_category'
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
    if 'matched_skills' in df_clean.columns:
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
        
        df_clean['matched_skills'] = df_clean['matched_skills'].apply(parse_skills)
    else:
        # Create empty matched_skills column if it doesn't exist
        df_clean['matched_skills'] = [[]] * len(df_clean)
    
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