#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Complete Scraper - Scrape All Occupations
===============================================

Automatically scrape all occupations, report progress every 10 minutes
Finally integrate all results and clean up temporary files

Author: Orange Team
Version: 1.0
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import json
from urllib.parse import urljoin
import logging
from datetime import datetime
import os
import glob

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalONETScraper:
    """Final O*NET Scraper - Scrape All Occupations"""
    
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
        
        # Technical skills keywords
        self.tech_skills = [
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'R', 'MATLAB', 'Go', 'Rust', 'Swift',
            'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask',
            'Spring', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy',
            'Apache Spark', 'Hadoop', 'Kubernetes', 'Docker', 'AWS', 'Azure', 'Google Cloud',
            'Git', 'Linux', 'Machine Learning', 'Deep Learning', 'Data Science', 'Big Data',
            'Cloud Computing', 'DevOps', 'Agile', 'Scrum', 'Tableau', 'Power BI', 'Excel',
            'MongoDB', 'PostgreSQL', 'MySQL', 'SQL', 'Apache Kafka', 'RabbitMQ',
            'Kotlin', 'Scala', 'PHP', 'Ruby', 'Perl', 'TypeScript', 'Dart',
            'Express.js', 'Laravel', 'ASP.NET', 'jQuery', 'Bootstrap',
            'Keras', 'OpenCV', 'NLTK', 'spaCy', 'Jenkins', 'GitLab CI', 'GitHub Actions',
            'Ansible', 'Chef', 'Puppet', 'Terraform', 'Apache Airflow'
        ]
        
        self.start_time = datetime.now()
        self.last_report_time = self.start_time
    
    def get_page(self, url, retries=3):
        """Get webpage content"""
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
                else:
                    logger.error(f"Unable to get page {url}: {e}")
        return None
    
    def get_all_occupation_links(self):
        """Get all occupation links"""
        logger.info("Starting to get all occupation links...")
        all_links = {}
        
        # Define all occupation families
        occupation_families = [
            (15, "Computer and Mathematical Occupations"),
            (13, "Business and Financial Operations"),
            (11, "Management Occupations"),
            (17, "Architecture and Engineering"),
            (19, "Life, Physical, and Social Science"),
            (21, "Community and Social Service"),
            (23, "Legal Occupations"),
            (25, "Education, Training, and Library"),
            (27, "Arts, Design, Entertainment, Sports, and Media"),
            (29, "Healthcare Practitioners and Technical"),
            (31, "Healthcare Support"),
            (33, "Protective Service"),
            (35, "Food Preparation and Serving Related"),
            (37, "Building and Grounds Cleaning and Maintenance"),
            (39, "Personal Care and Service"),
            (41, "Sales and Related"),
            (43, "Office and Administrative Support"),
            (45, "Farming, Fishing, and Forestry"),
            (47, "Construction and Extraction"),
            (49, "Installation, Maintenance, and Repair"),
            (51, "Production"),
            (53, "Transportation and Material Moving")
        ]
        
        for family_id, family_name in occupation_families:
            logger.info(f"Getting {family_name} occupation links...")
            url = f"{self.base_url}/find/family?f={family_id}&g=Go"
            
            soup = self.get_page(url)
            if not soup:
                logger.warning(f"Unable to get {family_name} page, skipping")
                continue
            
            # Try multiple selectors
            selectors = [
                'a[href*="/link/summary/"]',
                'td.report2 > a[href*="/link/summary/"]',
                'a[href*="/summary/"]'
            ]
            
            family_links = {}
            for selector in selectors:
                found_links = soup.select(selector)
                if found_links:
                    logger.info(f"Found {len(found_links)} links in {family_name} using selector '{selector}'")
                    for link in found_links:
                        title = link.get_text(strip=True)
                        href = link.get('href', '')
                        if title and href and 'summary' in href:
                            full_url = urljoin(self.base_url, href)
                            family_links[title] = full_url
                    break
            
            all_links.update(family_links)
            logger.info(f"{family_name}: Found {len(family_links)} occupations")
            
            # Add delay to avoid being blocked
            time.sleep(2)
        
        logger.info(f"Total found {len(all_links)} occupation links")
        return all_links
    
    def extract_occupation_info(self, soup, title):
        """Extract occupation information"""
        data = {
            'title': title,
            'description': '',
            'skills': [],
            'technology_skills': [],
            'education_level': '',
            'salary_median': '',
            'job_growth': '',
            'work_activities': [],
            'work_context': [],
            'knowledge_areas': [],
            'abilities': [],
            'work_styles': [],
            'tasks': [],
            'tools_used': [],
            'work_values': []
        }
        
        try:
            # Extract description
            page_text = soup.get_text()
            if page_text:
                paragraphs = soup.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if len(text) > 100 and any(keyword in text.lower() for keyword in ['analyze', 'develop', 'design', 'manage', 'implement', 'create', 'provide']):
                        data['description'] = text
                        break
            
            # Extract skill information
            page_text_lower = page_text.lower()
            for tech_skill in self.tech_skills:
                if tech_skill.lower() in page_text_lower:
                    data['technology_skills'].append(tech_skill)
            
            # Extract salary information
            salary_patterns = [
                r'\$[\d,]+(?:,\d{3})*(?:\.\d{2})?',
                r'[\d,]+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars?|USD)',
            ]
            
            for pattern in salary_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    data['salary_median'] = matches[0]
                    break
            
            # Extract work activities
            activity_items = soup.find_all(['li', 'p'])
            for item in activity_items[:5]:
                activity_text = item.get_text(strip=True)
                if activity_text and len(activity_text) > 20:
                    data['work_activities'].append(activity_text)
            
        except Exception as e:
            logger.error(f"Error extracting occupation information: {e}")
        
        return data
    
    def scrape_occupation_details(self, title, url):
        """Scrape detailed information for a single occupation"""
        soup = self.get_page(url)
        if not soup:
            return None
        
        data = self.extract_occupation_info(soup, title)
        data['url'] = url
        
        return data
    
    def should_report_progress(self):
        """Check if should report progress (every 10 minutes)"""
        current_time = datetime.now()
        if (current_time - self.last_report_time).total_seconds() >= 600:  # 10 minutes = 600 seconds
            self.last_report_time = current_time
            return True
        return False
    
    def report_progress(self, current, total, success_count, failed_count):
        """Report progress"""
        elapsed_time = datetime.now() - self.start_time
        progress_percent = (current / total) * 100
        estimated_remaining = (elapsed_time / current) * (total - current) if current > 0 else 0
        
        print(f"\n📊 Progress Report - {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Progress: {current}/{total} ({progress_percent:.1f}%)")
        print(f"   Success: {success_count}, Failed: {failed_count}")
        print(f"   Elapsed Time: {elapsed_time}")
        print(f"   Estimated Remaining: {estimated_remaining}")
        print(f"   Success Rate: {(success_count/(success_count+failed_count)*100):.1f}%" if (success_count+failed_count) > 0 else "0%")
    
    def scrape_all_occupations(self):
        """Scrape all occupation data"""
        logger.info("Starting to scrape all O*NET occupation data...")
        
        # Get all occupation links
        all_links = self.get_all_occupation_links()
        
        if not all_links:
            logger.error("Unable to get occupation links")
            return []
        
        logger.info(f"Starting to scrape {len(all_links)} occupations...")
        
        all_data = []
        failed_count = 0
        
        for i, (title, url) in enumerate(all_links.items(), 1):
            try:
                data = self.scrape_occupation_details(title, url)
                if data:
                    all_data.append(data)
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                logger.error(f"Error: {title} - {e}")
            
            # Add delay to avoid being blocked
            time.sleep(2)
            
            # Report progress every 10 minutes
            if self.should_report_progress():
                self.report_progress(i, len(all_links), len(all_data), failed_count)
            
            # Save intermediate results every 50 occupations
            if i % 50 == 0:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_file = f"temp_all_occupations_{timestamp}.json"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=2)
                logger.info(f"Intermediate results saved to: {temp_file}")
        
        # Final progress report
        self.report_progress(len(all_links), len(all_links), len(all_data), failed_count)
        
        logger.info(f"O*NET data scraping completed, obtained {len(all_data)} occupation data, failed {failed_count}")
        return all_data
    
    def load_existing_data(self):
        """Load existing data"""
        existing_data = []
        
        # Load existing 100 occupation data
        existing_files = [
            "100_occupations_20250920_000511.csv",
            "100_occupations_20250920_000659.csv"
        ]
        
        for file in existing_files:
            if os.path.exists(file):
                logger.info(f"Loading existing data: {file}")
                df = pd.read_csv(file)
                data = df.to_dict('records')
                existing_data.extend(data)
                logger.info(f"Loaded {len(data)} occupations from {file}")
        
        return existing_data
    
    def merge_all_data(self, new_data, existing_data):
        """Merge all data"""
        logger.info("Starting to merge all data...")
        
        # Merge data
        all_data = existing_data + new_data
        
        # Remove duplicates (based on title)
        seen_titles = set()
        unique_data = []
        for item in all_data:
            if item['title'] not in seen_titles:
                seen_titles.add(item['title'])
                unique_data.append(item)
        
        logger.info(f"Total data after merging: {len(unique_data)} occupations")
        return unique_data
    
    def save_final_results(self, all_data):
        """Save final results"""
        logger.info("Saving final results...")
        
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Export to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"all_occupations_complete_{timestamp}.csv"
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        logger.info(f"Final CSV file saved to: {csv_filename}")
        
        # Export to JSON
        json_filename = f"all_occupations_complete_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Final JSON file saved to: {json_filename}")
        
        # Display data overview
        print(f"\n📋 Final Data Overview:")
        print(f"   - Total Occupations: {len(df)}")
        print(f"   - Occupations with Descriptions: {len(df[df['description'].str.len() > 0])}")
        print(f"   - Occupations with Skills: {len(df[df['technology_skills'].apply(lambda x: len(x) > 0)])}")
        print(f"   - Occupations with Salary Info: {len(df[df['salary_median'].str.len() > 0)])}")
        print(f"   - Occupations with Work Activities: {len(df[df['work_activities'].apply(lambda x: len(x) > 0)])}")
        
        # Skills statistics
        all_skills = []
        for skills in df['technology_skills']:
            if isinstance(skills, list):
                all_skills.extend(skills)
        
        if all_skills:
            skill_counts = pd.Series(all_skills).value_counts()
            print(f"\n📊 Technical Skills Statistics (Top 20):")
            for skill, count in skill_counts.head(20).items():
                print(f"   {skill}: {count} times")
        
        return csv_filename, json_filename
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        logger.info("Cleaning up temporary files...")
        
        # Delete temporary files
        temp_patterns = [
            "temp_*_occupations_*.json",
            "temp_all_occupations_*.json"
        ]
        
        deleted_count = 0
        for pattern in temp_patterns:
            temp_files = glob.glob(pattern)
            for file in temp_files:
                try:
                    os.remove(file)
                    deleted_count += 1
                    logger.info(f"Deleted temporary file: {file}")
                except Exception as e:
                    logger.warning(f"Unable to delete file {file}: {e}")
        
        logger.info(f"Total deleted {deleted_count} temporary files")

def main():
    """Main function"""
    print("=" * 60)
    print("Final O*NET Scraper - Scrape All Occupations")
    print("=" * 60)
    
    # Create scraper instance
    scraper = FinalONETScraper()
    
    try:
        # Load existing data
        print("\n📂 Loading existing data...")
        existing_data = scraper.load_existing_data()
        print(f"Loaded {len(existing_data)} occupation data")
        
        # Scrape all data
        print("\n🚀 Starting to scrape all occupation data...")
        print("⚠️ Note: This may take a long time, progress will be reported every 10 minutes")
        
        new_data = scraper.scrape_all_occupations()
        
        if not new_data:
            print("❌ Scraping failed")
            return
        
        # Merge all data
        print("\n🔄 Merging all data...")
        all_data = scraper.merge_all_data(new_data, existing_data)
        
        # Save final results
        print("\n💾 Saving final results...")
        csv_file, json_file = scraper.save_final_results(all_data)
        
        # Clean up temporary files
        print("\n🧹 Cleaning up temporary files...")
        scraper.cleanup_temp_files()
        
        print(f"\n🎉 All occupation data scraping completed!")
        print(f"📊 Final results saved as:")
        print(f"   - CSV: {csv_file}")
        print(f"   - JSON: {json_file}")
        print(f"📊 Data saved in CSV and JSON formats, preserving original English content")
        
    except KeyboardInterrupt:
        print("\n⚠️ User interrupted the program")
    except Exception as e:
        print(f"\n❌ Program error: {e}")
        logger.error(f"Program error: {e}")

if __name__ == "__main__":
    main()
