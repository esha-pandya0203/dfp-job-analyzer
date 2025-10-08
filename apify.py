import csv
import re
from apify_client import ApifyClient

# ----------------------------
# CONFIGURATION
# ----------------------------
API_TOKEN = "apify_api_prNEOV3aUSk64I6mygzgp0tnT3LFD91ahlsN"
ACTOR_ID = "RIGGeqD6RqKmlVoQU"
LOCATION = "North America"
MAX_JOBS_PER_TITLE = 500
OUTPUT_FILE = "linkedIn_jobs.csv"  # 👈 one combined file

# Job categories and titles
JOB_CATEGORIES = {
    "Computer Programmers": ["AI/ML", "Cloud Engineer", "IT"],
    "Software Developers": ["Software Developer", "DevOps"],
    "Software Quality Assurance Analysts and Testers": ["Operations", "QA"],
    "Data Scientists": ["Data Analyst", "Data Scientist", "Data Engineer"],
    "Computer and Information Systems Managers": ["Technical Product Manager"],
    "Computer Network Architects": ["Cybersecurity", "Network engineers"]
}

# Job category codes (manual mapping)
JOB_CATEGORY_CODES = {
    "Computer Programmers": "15-1251",
    "Software Developers": "15-1252",
    "Software Quality Assurance Analysts and Testers": "15-1253",
    "Data Scientists": "15-2050",
    "Computer and Information Systems Managers": "11-3021",
    "Computer Network Architects": "15-1241"
}

# ----------------------------
# INITIALIZE APIFY CLIENT
# ----------------------------
client = ApifyClient(token=API_TOKEN)

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def parse_salary(salary_str):
    """Extract numeric salary min/max from text like '$50,000 - $70,000'."""
    if not salary_str:
        return None, None
    salary_str = salary_str.replace(",", "").strip()
    if "-" in salary_str:
        parts = salary_str.split("-")
        try:
            salary_min = int(re.findall(r"\d+", parts[0])[0])
            salary_max = int(re.findall(r"\d+", parts[1])[0])
            return salary_min, salary_max
        except IndexError:
            return None, None
    else:
        numbers = re.findall(r"\d+", salary_str)
        if not numbers:
            return None, None
        val = int(numbers[0])
        return val, val


def scrape_linkedin_jobs(title, location, max_jobs):
    """Scrape jobs from LinkedIn via Apify LinkedIn Jobs actor."""
    actor_input = {
        "searchStrings": [title],
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
        jobs_list.append({
            "job_category": "",
            "job_category_code": "",
            "job_title": item.get("title"),
            "description": item.get("description"),
            "posting_link": item.get("url"),
            "salary_min": salary_min,
            "salary_max": salary_max,
            "salary_range": item.get("salary"),
            "location": item.get("location"),
            "Experience Level": item.get("experienceLevel"),
        })
    return jobs_list


def save_jobs_to_csv(jobs, filename):
    """Save list of jobs to a single CSV file."""
    if not jobs:
        print("No jobs to save.")
        return
    keys = jobs[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(jobs)
    print(f"✅ Saved {len(jobs)} jobs to {filename}")


# ----------------------------
# MAIN SCRIPT
# ----------------------------
all_jobs = []

for category, titles in JOB_CATEGORIES.items():
    print(f"\nScraping category: {category}")
    job_code = JOB_CATEGORY_CODES.get(category, "N/A")
    for title in titles:
        print(f"  → Scraping title: {title}")
        jobs = scrape_linkedin_jobs(title, LOCATION, MAX_JOBS_PER_TITLE)
        # Tag category and code for each job
        for job in jobs:
            job["job_category"] = category
            job["job_category_code"] = job_code
        all_jobs.extend(jobs)

# Save everything to one file
save_jobs_to_csv(all_jobs, OUTPUT_FILE)

print("\n🎉 Scraping complete! Combined data saved in linkedIn_jobs.csv")
