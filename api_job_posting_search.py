import requests 
import time 
import pandas as pd 

'''
Pulls Job Postings from the Adzuna API 
'''

# constants 
APP_ID = 'a6e23083' 
APP_KEY = 'f3328d6385cdb511ae9ba9ba2f357c66'
API_URL = 'https://api.adzuna.com/v1/api/jobs/{country}/search/{page}' 
COUNTRY = 'us' 
RESULTS_PER_PAGE = 50 # limited by Adzuna 
MIN_RESULTS = 500 # per job title 

def fetch_jobs(title, location=None, min_results=50):
    print(f"\nFetching jobs for: '{title}'...")
    
    collected_jobs = [] 
    page = 1 

    while len(collected_jobs) < min_results: 
        url = API_URL.format(country=COUNTRY, page=page)
        params = {
            'app_id': APP_ID, 
            'app_key': APP_KEY, 
            'results_per_page': RESULTS_PER_PAGE, 
            'what': title, 
            'content-type': 'application/json'
        }

        if location: 
            params['where'] = location 
        
        response = requests.get(url, params=params)

        if response.status_code != 200: 
            print(f"Error: {response.status_code} - {response.text}")
            break 
        
        data = response.json() 
        results = data.get('results', [])
        if not results: 
            print(f"No more results for {title} on page {page}.")
            break 

        collected_jobs.extend(results)
        print(f"Collected {len(collected_jobs)} jobs so far for {title}")

        page += 1 
        time.sleep(1) # avoid hitting rate limits 
    
    return collected_jobs

def print_job_summaries(jobs): 
    for job in jobs: 
        print('Title:', job.get('title'))
        print('Company:', job.get('company', {}).get('display_name'))
        print('Location:', job.get('location', {}).get('display_name'))
        print('Category:', job.get('category', {}).get('label'))
        print('Salary:', job.get('salary_is_predicted', 0), '-', job.get('salary_min'), 'to', job.get('salary_max'))
        print('Description:', job.get('description'))
        print('Redirect URL:', job.get('redirect_url'))
        print('--------\n')

def jobs_to_dataframe(jobs): 
    """
    Create a dataframe for individual job titles 
    """
    job_dicts = [] 
    for job in jobs: 
        job_dict = {
            'title': job.get('title'), 
            'company': job.get('company', {}).get('display_name'), 
            'location': job.get('location', {}).get('display_name'), 
            'category': job.get('category', {}).get('label'), 
            'salary_min': job.get('salary_min'), 
            'salary_max': job.get('salary_max'), 
            'salary_predicted': job.get('salary_is_predicted'), 
            'description': job.get('description'), 
            'redirect_url': job.get('redirect_url')
        }

        job_dicts.append(job_dict)

    df = pd.DataFrame(job_dicts)
    return df 
    
if __name__ == '__main__':
    job_titles = [
        'Data Engineer', 
        'AI ML', 
        'IT', 
        'Technical Product Manager', 
        'DevOps'
    ]

    us_state = input("Enter U.S. state (or press Enter to search all of US): ").strip() 

    for title in job_titles:
        jobs = fetch_jobs(title, location=us_state if us_state else None, min_results=MIN_RESULTS)
        print(f"Total jobs fetched for {title}: {len(jobs)}")

        # convert to DataFrame 
        df = jobs_to_dataframe(jobs) 
        print(df.head()) 

        # save to csv file 
        csv_filename = f"{title.replace(' ', '_').lower()}_jobs.csv"
        df.to_csv(csv_filename, index=False)
        print(f"Saved data to {csv_filename}")