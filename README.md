# 🧠 LinkedIn Job Scraper + Skill Matcher (Apify Integration)

This project automates the process of **scraping job postings from LinkedIn** using the **Apify API**, then enhances the data by matching **technology skills** from the official `occupations_data.csv` dataset.

---

## 🚀 Features

* Scrapes **500 job postings** per job title using Apify’s LinkedIn Jobs Actor
* Supports **multiple job categories** and assigns **official occupation codes**
* Extracts **salary range, job level, description, and location**
* Matches **skills mentioned in job descriptions** against the official occupations database
* Saves results to a **CSV file** for analysis or visualization

---

## 🧩 Folder Structure

```
Aplify_Scraper/
│
├── newaPLIFY.PY                      # LinkedIn job scraper script
├── skills_matcher.py                 # Skill extraction + matching script
├── linkedin_jobs.csv                 # Output from the scraper
├── skills_matched_linkedin_jobs.csv  # Output after skill matching
├── occupations_data.csv              # Skills dataset used for matching
├── processed_jobs/                   # Optional output folder
└── README.md                         # You’re reading this!
```

---

## ⚙️ Setup Instructions

### 1️⃣ Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2️⃣ Install Dependencies

```bash
pip install apify-client pandas
```

### 3️⃣ Configure API Access

In `newaPLIFY.PY`, set your **Apify API Token** and **Actor ID**:

```python
API_TOKEN = "your_apify_api_token"
ACTOR_ID = "RIGGeqD6RqKmlVoQU"
```

---

## 🕵️‍♀️ Running the Scraper

The scraper pulls data for multiple job categories and saves it to one CSV file (`linkedin_jobs.csv`).

```bash
python newaPLIFY.PY
```

Each job entry includes:

* Job Title
* Description
* Salary Min / Max / Range
* Location
* Seniority Level
* Job Category & Category Code

---

## 🧠 Running the Skill Matcher

Once the scraper completes:

```bash
python skills_matcher.py
```

This script:

* Reads all **technology skills** from `occupations_data.csv`
* Compares them with the **job descriptions**
* Adds a column `Matched_Skills` to show all matched skills
* Saves output as:
  **`skills_matched_linkedin_jobs.csv`**

---

## 📊 Output Example

| job_category        | job_title       | location      | salary_min | salary_max | Matched_Skills               |
| ------------------- | --------------- | ------------- | ---------- | ---------- | ---------------------------- |
| Data Scientists     | Data Analyst    | New York, USA | 75000      | 110000     | ['python', 'sql', 'tableau'] |
| Software Developers | DevOps Engineer | Toronto, CA   | 90000      | 125000     | ['aws', 'docker', 'jenkins'] |

---

## 🧾 Job Category Codes

| Job Category                     | Code    |
| -------------------------------- | ------- |
| Computer Programmers             | 15-1251 |
| Software Developers              | 15-1252 |
| Software QA Analysts and Testers | 15-1253 |
| Data Scientists                  | 15-2050 |
| Computer & Info Systems Managers | 11-3021 |
| Computer Network Architects      | 15-1241 |

---

## ✅ Notes

* The Apify Actor `RIGGeqD6RqKmlVoQU` must be public and accessible.
* You can adjust the number of jobs per title via `MAX_JOBS_PER_TITLE`.
* Ensure `occupations_data.csv` contains the column `technology_skills`.
* Output files will be created automatically in your project directory.

---

**Created by:** Sumreen
**Purpose:** Automate large-scale LinkedIn job data collection and skill mapping for North American tech roles.
