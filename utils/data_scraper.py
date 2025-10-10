"""
------------------------------------------------------------
File: data_scraper.py
Team: Orange Team
Members: 
    - Jiatong Li (jiatong4)
    - Esha Pandya (epandya)
    - Fan Yang (fy4)
    - Sumreen Fathima (sumreenf)

Description:
    Code to make api requests to Adzuna endpoints and collect job postings, 
    cleaning up data before saving to respective files. 

Imports:
    - Imports from: csv, requests, time, pandas, os, re, utils 
    - Imported by: app.py
------------------------------------------------------------
"""

import csv
import requests 
import time 
import pandas as pd 
import os 
import re 
from apify_client import ApifyClient
from utils.job_title_mapping import match_job_title_to_soc_code 
from utils.skill_extractor import extract_skills

'''
Parse the given salary range and return the salary min and salary max 
'''
def parse_salary(salary_str):
    # Remove currency symbols, commas, and time-based suffixes
    salary_str = salary_str.replace(",", "")
    salary_str = re.sub(r"[\$/]", "", salary_str)
    salary_str = re.sub(r"(per\s*year|/yr|/year|annually)", "", salary_str, flags=re.IGNORECASE)
    salary_str = salary_str.strip()

    if "-" in salary_str:
        parts = salary_str.split("-")
        try:
            salary_min = float(re.findall(r"\d+(?:\.\d+)?", parts[0])[0])
            salary_max = float(re.findall(r"\d+(?:\.\d+)?", parts[1])[0])
            return int(salary_min), int(salary_max)  # Convert to int for consistency
        except (IndexError, ValueError):
            return None, None
    else:
        numbers = re.findall(r"\d+(?:\.\d+)?", salary_str)
        if not numbers:
            return None, None
        val = float(numbers[0])
        return int(val), int(val)

'''
Scrape jobs from LinkedIn via Apify LinkedIn Jobs actor.
'''
def scrape_linkedin_jobs(job_title, location, max_jobs, soc_code):
    # retrieve apify credentials 
    with open('utils/apify_credentials.csv', mode='r') as file: 
        reader = csv.DictReader(file)
        credentials = next(reader) 
        API_TOKEN = credentials['API_TOKEN']
        ACTOR_ID = credentials['ACTOR_ID']

    client = ApifyClient(token=API_TOKEN)

    actor_input = {
        "searchStrings": [job_title],
        "locations": [location],
        "maxJobs": max_jobs
    }

    run = client.actor(ACTOR_ID).call(run_input=actor_input)
    dataset_id = run["defaultDatasetId"]

    list_page = client.dataset(dataset_id).list_items(limit=max_jobs)
    items = list_page.items

    jobs_list = []
    for item in items:
        salary_min, salary_max = parse_salary(item.get("salary"))

        if isinstance(salary_min, (int, float)) and isinstance(salary_max, (int, float)):
            avg_salary = (salary_min + salary_max) / 2
        elif isinstance(salary_min, (int, float)):
            avg_salary = salary_min
        elif isinstance(salary_max, (int, float)):
            avg_salary = salary_max
        else:
            avg_salary = 'N/A'

        jobs_list.append({
            "title": item.get("title"),
            "company": item.get('companyName'), 
            "location": item.get("location"),
            "average_salary": avg_salary, 
            "description": item.get("description"),
            "redirect_url": item.get("applyUrl"),
            "experience_level": item.get("experienceLevel"),
            "soc_code": soc_code, 
            "job_category": job_title,
        })

    return jobs_list

'''
Pulls job postings from Appify 
'''
def scrape_from_apify(job_title, soc_code): 
    MAX_POSTINGS = 300 
    LOCATION = 'Pittsburgh, Pennsylvania'

    postings = scrape_linkedin_jobs(job_title, LOCATION, MAX_POSTINGS, soc_code) 
    postings_df = pd.DataFrame(postings) 
    postings_df['matched_skills'] = postings_df['description'].apply(extract_skills)

    column_headers = ["title", "company", "location", "avg_salary", "description", "redirect_url", "experience_level", "soc_code", "job_category", "matched_skills"]
    postings_df = postings_df.reindex(columns=column_headers)

    return postings_df

'''
Retrieves job listings from Adzuna for the given job title and maximum number of results. 
'''
def fetch_jobs(title, max_results=50, results_per_page=50):
    print(f"\nFetching jobs for: '{title}'...")

    API_URL = 'https://api.adzuna.com/v1/api/jobs/{country}/search/{page}' 
    DETAIL_URL = 'https://api.adzuna.com/v1/api/jobs/{country}/details/{job_id}'
    COUNTRY = 'us' 

    # retrieve API credentials 
    with open('utils/adzuna_credentials.csv', mode='r') as file: 
        reader = csv.DictReader(file)
        credentials = next(reader) 
        API_ID = credentials['API_ID']
        API_KEY = credentials['API_KEY']
    
    collected_jobs = [] 
    page = 1 

    # set up and request API call 
    while len(collected_jobs) < max_results: 
        url = API_URL.format(country=COUNTRY, page=page)
        params = {
            'app_id': API_ID, 
            'app_key': API_KEY, 
            'results_per_page': results_per_page, 
            'what': title, 
            'where': 'Pittsburgh', 
            'content-type': 'application/json', 
            'sort_by': 'date' 
        }
        
        response = requests.get(url, params=params)

        if response.status_code != 200: 
            print(f"Error: {response.status_code} - {response.text}")
            break 
        
        data = response.json() 
        results = data.get('results', [])
        if not results: 
            print(f"No more results for {title} on page {page}.")
            break 

        # add listing to all job postings 
        collected_jobs.extend(results)
        print(f"Collected {len(collected_jobs)} jobs so far for {title}")

        page += 1 
        time.sleep(1) # avoid hitting rate limits 

    return collected_jobs

'''
Converts collected jobs to a dataframe. 
'''
def jobs_to_dataframe(jobs, soc_code, job_title): 
    '''
    Create a dataframe for individual job titles 
    '''
    job_dicts = [] 
    for job in jobs: 
        salary_min = job.get('salary_min') 
        salary_max = job.get('salary_max')
        if isinstance(salary_min, (int, float)) and isinstance(salary_max, (int, float)):
            avg_salary = (salary_min + salary_max) / 2
        elif isinstance(salary_min, (int, float)):
            avg_salary = salary_min
        elif isinstance(salary_max, (int, float)):
            avg_salary = salary_max
        else:
            avg_salary = 'N/A'

        job_dict = {
            'title': job.get('title'), 
            'company': job.get('company', {}).get('display_name'), 
            'location': job.get('location', {}).get('display_name'), 
            'avg_salary': avg_salary, 
            'description': job.get('description'), 
            'redirect_url': job.get('redirect_url'), 
            'experience_level': 'N/A', 
            'soc_code': soc_code, 
            'job_category': job_title
        }

        job_dicts.append(job_dict)

    df = pd.DataFrame(job_dicts)
    df['matched_skills'] = df['description'].apply(extract_skills)
    return df 

'''
Fetches Job Postings from the Adzuna API 
'''

def scrape_from_adzuna(job_title, soc_code): 
    # constants 
    RESULTS_PER_PAGE = 50 # limited by Adzuna 
    MAX_RESULTS = 300 # per job title 

    # for title in job_titles:
    jobs = fetch_jobs(job_title, max_results=MAX_RESULTS, results_per_page=RESULTS_PER_PAGE)
    print(f"Total jobs fetched for {job_title}: {len(jobs)}")

    # convert to DataFrame 
    postings = jobs_to_dataframe(jobs, soc_code, job_title) 

    return postings 

def append_to_csv(filename, data, column_headers=None): 
    output_dir = 'data/processed_data'
    os.makedirs(output_dir, exist_ok=True) # ensures directory exists 

    full_path = os.path.join(output_dir, filename) 

    if os.path.exists(full_path): 
        data.to_csv(full_path, mode='a', header=False, index=False)
        print(f'Data appended to {filename}')
    else: 
        if column_headers: 
            data = data.reindex(columns=column_headers)
        data.to_csv(full_path, mode='w', header=True, index=False)
        print(f'Created new CSV file {filename} and added data')

'''
Removes all job listing files when application is run. 
'''
def clear_processed_data(): 
    folder = os.path.join('data', 'processed_data')
    if os.path.exists(folder):
        for file in os.listdir(folder): 
            file_path = os.path.join(folder, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print(f"✅ Cleared existing files in {folder}")

'''
Collect all job postings and save to csv files corresponding to BLS soc codes. 
'''
def collect_all_job_postings():
    ALL_JOBS = ['Software Developer', ' Technical Operations', 'QA', 'Cloud Engineer', 'Data Analyst', 'Data Scientist', 'Data Scientist', 'Cybersecurity', 'Network Engineer', 'Data Engineer', 'AI/ML', 'IT', 'Technical Product Manager', 'DevOps']
    indeed_job_titles = ['Software Developer', 'Operations', 'QA', 'Cloud Engineer', 'Data Analyst', 'Data Scientist', 'Data Scientist', 'Cybersecurity', 'Network Engineer']
    adzuna_job_titles = ['Data Engineer', 'AI/ML', 'IT', 'Technical Product Manager', 'DevOps'] 

    column_headers = ["title", "company", "location", "avg_salary", "description", "redirect_url", "experience_level", "soc_code", "job_category", "matched_skills"] 

    for job_title in ALL_JOBS:
        soc_code = match_job_title_to_soc_code(job_title)
        print(f'Found soc code {soc_code} for {job_title}')

        if job_title in indeed_job_titles: 
            job_listings = scrape_from_apify(job_title, soc_code)
        elif job_title in adzuna_job_titles: 
            job_listings = scrape_from_adzuna(job_title, soc_code)
        
        append_to_csv(f"{soc_code}.csv", job_listings, column_headers)