#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Job Data Scraper
================

A utility scraper for collecting job market data from various sources.

Author: Fan Yang (CMU)
Version: 1.0
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import json
from urllib.parse import urljoin, urlparse
import logging
from datetime import datetime
import os
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobScraper:
    """Job Data Scraper for collecting employment data"""
    
    def __init__(self):
        self.base_url = "https://www.onetonline.org"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Job categories for filtering
        self.job_categories = {
            'software': ['Software Engineer', 'Developer', 'Programmer', 'Software Developer'],
            'data': ['Data Scientist', 'Data Analyst', 'Data Engineer', 'Business Analyst'],
            'ai': ['AI Engineer', 'Machine Learning Engineer', 'AI Researcher', 'ML Engineer'],
            'cybersecurity': ['Security Engineer', 'Cybersecurity Analyst', 'Security Consultant'],
            'devops': ['DevOps Engineer', 'Site Reliability Engineer', 'Platform Engineer'],
            'product': ['Product Manager', 'Product Owner', 'Product Analyst'],
            'design': ['UX Designer', 'UI Designer', 'Product Designer', 'UX Researcher']
        }
        
        self.start_time = datetime.now()
    
    def get_page(self, url, retries=3):
        """Get webpage content with retry mechanism"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup
            except requests.exceptions.Timeout as e:
                logger.warning(f"Request timeout (attempt {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(5)
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        
        logger.error(f"Failed to get page after {retries} attempts: {url}")
        return None
    
    def scrape_occupation_list(self):
        """Scrape occupation list from O*NET"""
        logger.info("Scraping occupation list...")
        
        # Get main occupation list page
        url = f"{self.base_url}/find/quick"
        soup = self.get_page(url)
        
        if not soup:
            return []
        
        occupations = []
        
        # Find occupation links
        occupation_links = soup.find_all('a', href=re.compile(r'/link/summary/'))
        
        for link in occupation_links[:50]:  # Limit to first 50 for demo
            try:
                title = link.get_text(strip=True)
                href = link.get('href')
                if title and href:
                    full_url = urljoin(self.base_url, href)
                    occupations.append({
                        'title': title,
                        'url': full_url,
                        'code': href.split('/')[-1] if '/' in href else ''
                    })
            except Exception as e:
                logger.warning(f"Error processing occupation link: {e}")
                continue
        
        logger.info(f"Found {len(occupations)} occupations")
        return occupations
    
    def scrape_occupation_details(self, occupation):
        """Scrape detailed information for a specific occupation"""
        try:
            soup = self.get_page(occupation['url'])
            if not soup:
                return None
            
            details = {
                'title': occupation['title'],
                'code': occupation['code'],
                'url': occupation['url'],
                'description': '',
                'skills': [],
                'education': '',
                'salary': '',
                'employment': ''
            }
            
            # Extract description
            desc_elem = soup.find('div', class_='summary')
            if desc_elem:
                details['description'] = desc_elem.get_text(strip=True)
            
            # Extract skills
            skills_section = soup.find('div', {'id': 'skills'})
            if skills_section:
                skill_items = skills_section.find_all('a')
                details['skills'] = [item.get_text(strip=True) for item in skill_items[:10]]
            
            # Extract education requirements
            edu_section = soup.find('div', {'id': 'education'})
            if edu_section:
                details['education'] = edu_section.get_text(strip=True)[:200]
            
            # Extract salary information
            salary_section = soup.find('div', {'id': 'wages'})
            if salary_section:
                details['salary'] = salary_section.get_text(strip=True)[:100]
            
            return details
            
        except Exception as e:
            logger.warning(f"Error scraping occupation details for {occupation['title']}: {e}")
            return None
    
    def scrape_data(self):
        """Main scraping function"""
        logger.info("Starting job data scraping...")
        
        # Get occupation list
        occupations = self.scrape_occupation_list()
        
        if not occupations:
            logger.error("No occupations found")
            return False
        
        # Scrape details for each occupation
        all_data = []
        failed_count = 0
        
        for i, occupation in enumerate(occupations):
            try:
                logger.info(f"Scraping {i+1}/{len(occupations)}: {occupation['title']}")
                
                details = self.scrape_occupation_details(occupation)
                if details:
                    all_data.append(details)
                else:
                    failed_count += 1
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.warning(f"Error processing {occupation['title']}: {e}")
                failed_count += 1
                continue
        
        # Save results
        if all_data:
            self.save_results(all_data)
            logger.info(f"Scraping completed: {len(all_data)} occupations, {failed_count} failed")
            return True
        else:
            logger.error("No data collected")
            return False
    
    def save_results(self, data):
        """Save scraped data to files"""
        logger.info("Saving results...")
        
        # Create data directory if it doesn't exist
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Save to CSV
        csv_filename = os.path.join(data_dir, "Job_Data.csv")
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        logger.info(f"Job data CSV saved to: {csv_filename}")
        
        # Save to JSON
        json_filename = os.path.join(data_dir, "Job_Data.json")
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Job data JSON saved to: {json_filename}")
        
        # Display summary
        print(f"\n📋 Job Data Summary:")
        print(f"   - Total Occupations: {len(df)}")
        print(f"   - With Descriptions: {len(df[df['description'].str.len() > 0])}")
        print(f"   - With Skills: {len(df[df['skills'].apply(lambda x: len(x) > 0)])}")
        print(f"   - With Education Info: {len(df[df['education'].str.len() > 0])}")
        print(f"   - With Salary Info: {len(df[df['salary'].str.len() > 0])}")
        
        return csv_filename, json_filename

if __name__ == "__main__":
    scraper = JobScraper()
    scraper.scrape_data()
