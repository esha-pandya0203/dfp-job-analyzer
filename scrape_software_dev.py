import asyncio
import csv
import random
from playwright.async_api import async_playwright

BASE_URL = "https://www.indeed.com"
JOB_TITLE = "software developer"
MAX_POSTINGS = 300
OUTPUT_FILE = "software_developer_jobs_USA_full.csv"


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


async def scrape_jobs():
    postings = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        start = 0
        while len(postings) < MAX_POSTINGS:
            search_url = f"{BASE_URL}/jobs?q={JOB_TITLE.replace(' ', '+')}&sort=date&start={start}"
            print(f"\n🔎 Visiting {search_url}")
            await page.goto(search_url, timeout=60000)
            await page.wait_for_timeout(random.uniform(4000, 6000))

            job_cards = await page.query_selector_all("div.job_seen_beacon")
            if not job_cards:
                print("⚠️ No job cards found (CAPTCHA or end of results). Stopping.")
                break

            print(f"  -> Found {len(job_cards)} jobs on this page.")

            for job in job_cards:
                if len(postings) >= MAX_POSTINGS:
                    break

                try:
                    title_el = await job.query_selector("h2.jobTitle span")
                    link_el = await job.query_selector("h2.jobTitle a")
                    location_el = await job.query_selector("div.companyLocation")
                    salary_el = await job.query_selector("div.metadata.salary-snippet-container")

                    title = await title_el.inner_text() if title_el else "N/A"
                    link = BASE_URL + (await link_el.get_attribute("href")) if link_el else "N/A"
                    location = await location_el.inner_text() if location_el else "N/A"
                    salary = await salary_el.inner_text() if salary_el else "Not Specified"

                    # Open detail page for description
                    desc_page = await context.new_page()
                    await desc_page.goto(link, timeout=60000)
                    await desc_page.wait_for_timeout(random.uniform(2000, 4000))

                    desc_el = await desc_page.query_selector("#jobDescriptionText")
                    description = await desc_el.inner_text() if desc_el else "Description not found"
                    await desc_page.close()

                    level = infer_level(title, description)

                    postings.append({
                        "title": title,
                        "description": description,
                        "url": link,
                        "salary_range": salary,
                        "location": location,
                        "level": level
                    })

                    print(f"    ✅ {title[:50]}... | {location} | {level}")

                except Exception as e:
                    print(f"    ⚠️ Skipped one job due to error: {e}")

            start += 15
            await page.wait_for_timeout(random.uniform(5000, 9000))

        await browser.close()

    # Save results to CSV
    if postings:
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["title", "description", "url", "salary_range", "location", "level"]
            )
            writer.writeheader()
            writer.writerows(postings)

        print(f"\n🎉 Saved {len(postings)} postings to {OUTPUT_FILE}")
    else:
        print("\n⚠️ No jobs were scraped.")


if __name__ == "__main__":
    asyncio.run(scrape_jobs())
