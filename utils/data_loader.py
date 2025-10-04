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