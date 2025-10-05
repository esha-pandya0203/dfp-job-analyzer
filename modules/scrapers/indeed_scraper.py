#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Indeed Job Scraper
==================

A scraper for collecting job postings from Indeed.com using Playwright.

Author: Fan Yang (CMU)
Version: 1.0
"""

import asyncio
import csv
import random
import pandas as pd
import os
from playwright.async_api import async_playwright

class IndeedScraper:
    """Indeed job scraper using Playwright"""
    
    def __init__(self, max_postings=300):
        self.base_url = "https://www.indeed.com"
        self.max_postings = max_postings
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def infer_level(self, title, description):
        """Infer experience level from title and description"""
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

    async def scrape_jobs(self, job_title, soc_code=None):
        """Scrape jobs for a specific title"""
        postings = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            start = 0
            while len(postings) < self.max_postings:
                search_url = f"{self.base_url}/jobs?q={job_title.replace(' ', '+')}&sort=date&start={start}"
                print(f"\n🔎 Visiting {search_url}")
                await page.goto(search_url, timeout=60000)
                await page.wait_for_timeout(random.uniform(4000, 6000))

                job_cards = await page.query_selector_all("div.job_seen_beacon")
                if not job_cards:
                    print("⚠️ No job cards found (CAPTCHA or end of results). Stopping.")
                    break

                print(f"  -> Found {len(job_cards)} jobs on this page.")

                for job in job_cards:
                    if len(postings) >= self.max_postings:
                        break

                    try:
                        title_el = await job.query_selector("h2.jobTitle span")
                        link_el = await job.query_selector("h2.jobTitle a")
                        location_el = await job.query_selector("div.companyLocation")
                        salary_el = await job.query_selector("div.metadata.salary-snippet-container")

                        title = await title_el.inner_text() if title_el else "N/A"
                        link = self.base_url + (await link_el.get_attribute("href")) if link_el else "N/A"
                        location = await location_el.inner_text() if location_el else "N/A"
                        salary = await salary_el.inner_text() if salary_el else "Not Specified"

                        # Open detail page for description
                        desc_page = await context.new_page()
                        await desc_page.goto(link, timeout=60000)
                        await desc_page.wait_for_timeout(random.uniform(2000, 4000))

                        desc_el = await desc_page.query_selector("#jobDescriptionText")
                        description = await desc_el.inner_text() if desc_el else "Description not found"
                        await desc_page.close()

                        level = self.infer_level(title, description)

                        postings.append({
                            "title": title,
                            "description": description,
                            "url": link,
                            "salary_range": salary,
                            "location": location,
                            "level": level,
                            "soc_code": soc_code
                        })

                        print(f"    ✅ {title[:50]}... | {location} | {level}")

                    except Exception as e:
                        print(f"    ⚠️ Skipped one job due to error: {e}")

                start += 15
                await page.wait_for_timeout(random.uniform(5000, 9000))

            await browser.close()

        return postings

    def scrape_and_save(self, job_title, soc_code=None, output_file=None):
        """Scrape jobs and save to CSV"""
        if output_file is None:
            output_file = f"{job_title.replace(' ', '_')}_jobs.csv"
        
        postings = asyncio.run(self.scrape_jobs(job_title, soc_code))
        
        if postings:
            df = pd.DataFrame(postings)
            output_path = os.path.join(self.data_dir, output_file)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"\n🎉 Saved {len(postings)} postings to {output_path}")
            return True
        else:
            print("\n⚠️ No jobs were scraped.")
            return False
