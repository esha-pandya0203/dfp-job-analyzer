# Indeed Job Scraper (Playwright)

This project scrapes **Software Developer** job postings from [Indeed.com](https://www.indeed.com) for the **USA**, collecting up to 500 recent postings.  
The scraper extracts:

- Job Title  
- Full Description  
- Posting Link URL  
- Salary Range  
- Location  
- Job Level (Entry-Level, Experienced, Internship – inferred from text)  

All results are saved into a CSV file.

---

## 🚀 Setup

1. **Clone this repo** or copy the script to your project folder.

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Mac/Linux
   venv\Scripts\activate      # Windows


3. **Install dependencies**
    pip3 install -r requirements.txt

4. **Install Playwright browsers**
    playwright install


**▶️ Run the Scraper**
    python3 scrape_software_dev.py

The script will:

Open Indeed search results (q=software+developer, sort=date)
Visit each job card and fetch details
Save them to software_developer_jobs_USA_full.csv
Repeat this for other Job Titles

**⚠️ Notes**

Playwright runs a real browser, so scraping may be slower but more reliable than Selenium.
Random delays are added between requests to reduce the chance of being blocked.
If a CAPTCHA appears, complete it manually in the opened browser window.


**🛠️ Customization**

Change the search keyword by updating:
    JOB_TITLE = "software developer"

Change the number of postings:
    MAX_POSTINGS = 300


**✅ Requirements**

Python 3.9+
Internet connection
Indeed.com accessible in your region

---

**Why not BeautifulSoup?**

We didn’t use BeautifulSoup because:

1. Indeed blocks static scraping easily
- If you just fetch the raw HTML with requests and parse it using BeautifulSoup, you’ll often hit blank pages or CAPTCHA walls.
- That’s what was happening when I got "no job cards found" — Indeed serves dynamic content that isn’t always visible in plain HTML.

2. Playwright handles JavaScript rendering
- Indeed loads many job details dynamically via JavaScript.
- Playwright controls a real browser, so the page fully loads and you can reliably query job postings.

3. Cleaner element targeting
- Instead of parsing HTML trees with BeautifulSoup, Playwright lets us directly select elements (like div.job_seen_beacon) and extract text/attributes.
- This reduces the risk of scraping empty content because Playwright “sees” what the browser sees.

4. Avoid duplication
- If we added BeautifulSoup on top of Playwright, it would just complicate things (we’d first render with Playwright, then re-parse with BeautifulSoup). Playwright’s selectors are powerful enough to replace the parsing step.

** 💡 So: **
Playwright = browser automation + scraping
BeautifulSoup = static HTML parsing

Since Indeed is highly dynamic, Playwright is the more reliable choice.
