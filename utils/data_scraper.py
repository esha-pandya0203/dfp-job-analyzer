import asyncio
import csv
import random
import requests 
import time 
import pandas as pd 
import os 
from playwright.async_api import async_playwright
from utils.job_title_mapping import match_job_title_to_soc_code 
from utils.skill_extractor import extract_skills

'''
Determine the experience level for the provided job given its title and description. 
'''
def infer_level(title, description):
    t = title.lower()
    d = description.lower()

    if any(k in t for k in ["intern", "internship", "co-op"]):
        return "Internship"
    if any(k in t for k in ["entry", "junior", "graduate", "associate"]):
        return "Entry-Level"
    if any(k in t for k in ["senior", "sr.", "lead", "principal", "staff", "manager"]):
        return "Experienced"
    if "entry level" in d or "recent graduate" in d:
        return "Entry-Level"
    if any(k in d for k in ["5+ years", "senior", "lead", "expert", "principal"]):
        return "Experienced"
    return "Not Specified"

'''
Find all job postings from Indeed for given job titles (limit to maximum number of postings). 
'''
async def scrape_jobs(job_title, soc_code, max_postings=300):
    postings = []

    BASE_URL = "https://www.indeed.com"

    # open webpage 
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # search for provided job title 
        start = 0
        while len(postings) < max_postings:
            search_url = f"{BASE_URL}/jobs?q={job_title.replace(' ', '+')}&sort=date&start={start}"
            print(f"\n🔎 Visiting {search_url}")
            await page.goto(search_url, timeout=60000)
            await page.wait_for_timeout(random.uniform(4000, 6000))

            job_cards = await page.query_selector_all("div.job_seen_beacon")
            if not job_cards:
                print("⚠️ No job cards found (CAPTCHA or end of results). Stopping.")
                break

            print(f"  -> Found {len(job_cards)} jobs on this page.")

            for job in job_cards:
                if len(postings) >= max_postings:
                    break

                # scrape job specific information 
                try:
                    title_el = await job.query_selector("h2.jobTitle span")
                    link_el = await job.query_selector("h2.jobTitle a")
                    location_el = await job.query_selector("div.companyLocation")
                    salary_el = await job.query_selector("div.metadata.salary-snippet-container")

                    title = await title_el.inner_text() if title_el else "N/A"
                    link = BASE_URL + (await link_el.get_attribute("href")) if link_el else "N/A"
                    location = await location_el.inner_text() if location_el else "N/A"
                    salary = await salary_el.inner_text() if salary_el else "Not Specified"

                    average_salary = 'Not Found' 
                    # parse salary range 
                    # if '-' in salary:
                    #     try:
                    #         parts = salary.replace("$", "").replace(",", "").split('-')
                    #         min_salary = int(parts[0].strip())
                    #         max_salary = int(parts[1].split()[0].strip())
                    #         avg_salary = (min_salary + max_salary) / 2
                    #     except Exception as e:
                    #         print(f"      ⚠️ Failed to parse salary range '{salary}': {e}")
                    # elif salary.startswith("$"):
                    #     try:
                    #         avg_salary = int(salary.replace("$", "").replace(",", "").split()[0])
                    #     except Exception as e:
                    #         print(f"      ⚠️ Failed to parse single salary '{salary}': {e}")

                    # Open detail page for description
                    desc_page = await context.new_page()
                    await desc_page.goto(link, timeout=60000)
                    await desc_page.wait_for_timeout(random.uniform(2000, 4000))

                    desc_el = await desc_page.query_selector("#jobDescriptionText")
                    description = await desc_el.inner_text() if desc_el else "Description not found"
                    await desc_page.close()

                    level = infer_level(title, description)

                    # append to dictionary for all postings 
                    postings.append({
                        "title": title,
                        "company": 'Not Found', 
                        "location": location, 
                        "average_salary": salary, 
                        "description": description,
                        "redirect_url": link,
                        "experience_level": level, 
                        "soc_code": soc_code, 
                        "job_category": job_title
                    })

                    print(f"    ✅ {title[:50]}... | {location} | {level}")

                except Exception as e:
                    print(f"    ⚠️ Skipped one job due to error: {e}")

            start += 15
            await page.wait_for_timeout(random.uniform(5000, 9000))

        await browser.close()
    
    return postings 

'''
Pulls job postings from Indeed 
'''
def scrape_from_indeed(job_title, soc_code): 
    MAX_POSTINGS = 300

    # scrape job postings 
    postings = asyncio.run(scrape_jobs(job_title, soc_code, MAX_POSTINGS))

    postings = pd.DataFrame(postings) 

    column_headers = ["title", "company", "location", "avg_salary", "description", "redirect_url", "experience_level", "soc_code", "job_category", "matched_skills"]
    postings = postings.reindex(columns=column_headers)
    return postings

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
            avg_salary = None  # Or 0, or skip, depending on your needs

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
    ALL_JOBS = ['Software Developer', 'Operations', 'QA', 'Cloud Engineer', 'Data Analyst', 'Data Scientist', 'Data Scientist', 'Cybersecurity', 'Network Engineer', 'Data Engineer', 'AI ML', 'IT', 'Technical Product Manager', 'DevOps']
    indeed_job_titles = ['Software Developer', 'Operations', 'QA', 'Cloud Engineer', 'Data Analyst', 'Data Scientist', 'Data Scientist', 'Cybersecurity', 'Network Engineer']
    adzuna_job_titles = ['Data Engineer', 'AI/ML', 'IT', 'Technical Product Manager', 'DevOps'] 

    column_headers = ["title", "company", "location", "avg_salary", "description", "redirect_url", "experience_level", "soc_code", "job_category", "matched_skills"] 

    for job_title in adzuna_job_titles:
        soc_code = match_job_title_to_soc_code(job_title)
        print(f'Found soc code {soc_code} for {job_title}')

        if job_title in indeed_job_titles: 
            job_listings = scrape_from_indeed(job_title, soc_code)
        elif job_title in adzuna_job_titles: 
            job_listings = scrape_from_adzuna(job_title, soc_code)
        
        append_to_csv(f"{soc_code}.csv", job_listings, column_headers)