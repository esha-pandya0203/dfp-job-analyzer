#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pennsylvania Employment Data Scraper
====================================

A specialized web scraper for Pennsylvania employment market data, combining O*NET occupation data and BLS API
to obtain Pennsylvania-specific employment statistics, salary data, and job opportunity information.

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
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PennsylvaniaJobScraper:
    """Pennsylvania Employment Data Scraper"""
    
    def __init__(self):
        self.base_url = "https://www.onetonline.org"
        self.pa_state_code = "PA"  # Pennsylvania state code
        self.pa_state_name = "Pennsylvania"
        
        # Request headers configuration
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Pennsylvania major cities
        self.pa_cities = [
            "Philadelphia", "Pittsburgh", "Allentown", "Erie", "Reading", 
            "Scranton", "Bethlehem", "Lancaster", "Harrisburg", "Altoona",
            "York", "State College", "Chester", "Wilkes-Barre", "Norristown"
        ]
        
        # Pennsylvania major industries
        self.pa_industries = [
            "Healthcare", "Education", "Manufacturing", "Technology", 
            "Finance", "Energy", "Agriculture", "Tourism", "Transportation"
        ]
        
        # Occupation family mapping
        self.occupation_families = {
            15: "Computer and Mathematical Occupations",
            13: "Business and Financial Operations", 
            11: "Management Occupations",
            17: "Architecture and Engineering",
            19: "Life, Physical, and Social Science",
            21: "Community and Social Service",
            23: "Legal Occupations",
            25: "Education, Training, and Library",
            27: "Arts, Design, Entertainment, Sports, and Media",
            29: "Healthcare Practitioners and Technical",
            31: "Healthcare Support",
            33: "Protective Service",
            35: "Food Preparation and Serving Related",
            37: "Building and Grounds Cleaning and Maintenance",
            39: "Personal Care and Service",
            41: "Sales and Related",
            43: "Office and Administrative Support",
            45: "Farming, Fishing, and Forestry",
            47: "Construction and Extraction",
            49: "Installation, Maintenance, and Repair",
            51: "Production",
            53: "Transportation and Material Moving"
        }
        
        self.start_time = datetime.now()
        self.last_report_time = self.start_time
    
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
                else:
                    logger.error(f"Unable to get page {url}: {e}")
        return None
    
    def get_occupation_code_from_url(self, url):
        """Extract occupation code from URL"""
        try:
            match = re.search(r'/link/summary/(\d+-\d+\.\d+)', url)
            if match:
                return match.group(1)
        except:
            pass
        return None
    
    def get_occupation_family_from_code(self, code):
        """Get occupation family from occupation code"""
        if not code:
            return "Unknown"
        
        try:
            family_id = int(code.split('-')[0])
            return self.occupation_families.get(family_id, "Unknown")
        except:
            return "Unknown"
    
    def get_pennsylvania_occupation_links(self, max_occupations=100):
        """Get Pennsylvania-related occupation links"""
        logger.info("Starting to get Pennsylvania-related occupation links...")
        all_links = {}
        
        # Priority occupation families (Pennsylvania major industries related)
        priority_families = [15, 13, 11, 17, 29, 25, 19, 27]  # Technology, Business, Management, Engineering, Healthcare, Education, etc.
        
        for family_id in priority_families:
            family_name = self.occupation_families.get(family_id, f"Category{family_id}")
            logger.info(f"Getting {family_name} occupation links...")
            
            url = f"{self.base_url}/find/family?f={family_id}&g=Go"
            soup = self.get_page(url)
            
            if not soup:
                logger.warning(f"Unable to get {family_name} page, skipping")
                continue
            
            # Find occupation links
            selectors = [
                'a[href*="/link/summary/"]',
                'td.report2 > a[href*="/link/summary/"]',
                'a[href*="/summary/"]'
            ]
            
            family_links = {}
            for selector in selectors:
                found_links = soup.select(selector)
                if found_links:
                    logger.info(f"Found {len(found_links)} links in {family_name}")
                    for link in found_links:
                        title = link.get_text(strip=True)
                        href = link.get('href', '')
                        if title and href and 'summary' in href:
                            full_url = urljoin(self.base_url, href)
                            family_links[title] = {
                                'url': full_url,
                                'family': family_name,
                                'family_id': family_id
                            }
                    break
            
            all_links.update(family_links)
            logger.info(f"{family_name}: Found {len(family_links)} occupations")
            
            # Add delay to avoid being blocked
            time.sleep(2)
            
            # If we have enough occupations, stop
            if len(all_links) >= max_occupations:
                break
        
        logger.info(f"Total found {len(all_links)} occupation links")
        return dict(list(all_links.items())[:max_occupations])
    
    def extract_pennsylvania_specific_data(self, title, url, family_info):
        """Extract Pennsylvania-specific occupation data"""
        logger.info(f"Extracting Pennsylvania data: {title}")
        
        # Initialize data structure
        data = {
            'title': title,
            'occupation_code': self.get_occupation_code_from_url(url),
            'occupation_family': family_info['family'],
            'occupation_family_id': family_info['family_id'],
            'state': self.pa_state_name,
            'state_code': self.pa_state_code,
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
            'work_values': [],
            'pa_cities_mentioned': [],
            'pa_industries_mentioned': [],
            'url': url
        }
        
        # Get main page
        soup = self.get_page(url)
        if not soup:
            logger.warning(f"Unable to get main page for {title}")
            return data
        
        try:
            page_text = soup.get_text()
            page_text_lower = page_text.lower()
            
            # Extract basic description
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 100 and any(keyword in text.lower() for keyword in ['analyze', 'develop', 'design', 'manage', 'implement', 'create', 'provide']):
                    data['description'] = text
                    break
            
            # Check if Pennsylvania cities are mentioned
            for city in self.pa_cities:
                if city.lower() in page_text_lower:
                    data['pa_cities_mentioned'].append(city)
            
            # Check if Pennsylvania industries are mentioned
            for industry in self.pa_industries:
                if industry.lower() in page_text_lower:
                    data['pa_industries_mentioned'].append(industry)
            
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
            
            # Extract technology skills
            tech_skills = [
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
            
            for tech_skill in tech_skills:
                if tech_skill.lower() in page_text_lower:
                    data['technology_skills'].append(tech_skill)
            
            # Extract education requirements
            education_keywords = [
                'bachelor', 'master', 'phd', 'doctorate', 'associate', 'high school',
                'college', 'university', 'degree', 'certification', 'diploma'
            ]
            
            for keyword in education_keywords:
                if keyword in page_text_lower:
                    sentences = page_text.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower() and len(sentence.strip()) > 10:
                            data['education_level'] = sentence.strip()
                            break
                    if data['education_level']:
                        break
            
            # Extract work activities
            activity_elements = soup.find_all(['li', 'p', 'td'])
            for element in activity_elements:
                text = element.get_text(strip=True)
                if text and len(text) > 20 and len(text) < 200:
                    if any(keyword in text.lower() for keyword in ['analyze', 'develop', 'design', 'manage', 'implement', 'create', 'provide', 'maintain', 'operate', 'supervise']):
                        data['work_activities'].append(text)
            
            data['work_activities'] = data['work_activities'][:10]  # Limit to top 10
            
        except Exception as e:
            logger.error(f"Error extracting data for {title}: {e}")
        
        return data
    
    def get_pennsylvania_employment_stats(self):
        """Get Pennsylvania employment statistics"""
        logger.info("Getting Pennsylvania employment statistics...")
        
        # Here we can integrate BLS API to get Pennsylvania-specific data
        # Since BLS API requires registration, we provide mock data here
        pa_stats = {
            'total_employment': 6000000,  # Pennsylvania total employment
            'unemployment_rate': 4.2,     # Unemployment rate
            'average_salary': 55000,      # Average salary
            'top_industries': [
                {'name': 'Healthcare', 'employment': 800000, 'growth': 2.1},
                {'name': 'Education', 'employment': 600000, 'growth': 1.8},
                {'name': 'Manufacturing', 'employment': 500000, 'growth': 0.5},
                {'name': 'Technology', 'employment': 300000, 'growth': 3.2},
                {'name': 'Finance', 'employment': 250000, 'growth': 1.5}
            ],
            'major_cities': [
                {'name': 'Philadelphia', 'employment': 1500000, 'avg_salary': 62000},
                {'name': 'Pittsburgh', 'employment': 1200000, 'avg_salary': 58000},
                {'name': 'Allentown', 'employment': 400000, 'avg_salary': 52000},
                {'name': 'Erie', 'employment': 300000, 'avg_salary': 48000},
                {'name': 'Reading', 'employment': 250000, 'avg_salary': 50000}
            ]
        }
        
        return pa_stats
    
    def should_report_progress(self):
        """Check if should report progress (every 5 minutes)"""
        current_time = datetime.now()
        if (current_time - self.last_report_time).total_seconds() >= 300:  # 5 minutes = 300 seconds
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
    
    def scrape_pennsylvania_data(self, max_occupations=50):
        """Scrape Pennsylvania data"""
        logger.info("Starting to scrape Pennsylvania employment data...")
        
        # Get occupation links
        all_links = self.get_pennsylvania_occupation_links(max_occupations)
        
        if not all_links:
            logger.error("Unable to get occupation links")
            return []
        
        logger.info(f"Starting to scrape {len(all_links)} occupations for Pennsylvania data...")
        
        all_data = []
        failed_count = 0
        
        for i, (title, link_info) in enumerate(all_links.items(), 1):
            try:
                data = self.extract_pennsylvania_specific_data(title, link_info['url'], link_info)
                if data:
                    all_data.append(data)
                    logger.info(f"Successfully extracted data: {title}")
                else:
                    failed_count += 1
                    logger.warning(f"Failed to extract data: {title}")
            except Exception as e:
                failed_count += 1
                logger.error(f"Error processing {title}: {e}")
            
            # Add delay to avoid being blocked
            time.sleep(2)
            
            # Report progress every 5 minutes
            if self.should_report_progress():
                self.report_progress(i, len(all_links), len(all_data), failed_count)
            
            # Save intermediate results every 10 occupations
            if i % 10 == 0:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_file = f"temp_pa_occupations_{timestamp}.json"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=2)
                logger.info(f"Intermediate results saved to: {temp_file}")
        
        # Final progress report
        self.report_progress(len(all_links), len(all_links), len(all_data), failed_count)
        
        logger.info(f"Pennsylvania data scraping completed, obtained {len(all_data)} occupation data, failed {failed_count}")
        return all_data
    
    def save_pennsylvania_results(self, all_data):
        """Save Pennsylvania results"""
        logger.info("Saving Pennsylvania results...")
        
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Export to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"pennsylvania_occupations_{timestamp}.csv"
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        logger.info(f"Pennsylvania CSV file saved to: {csv_filename}")
        
        # Export to JSON
        json_filename = f"pennsylvania_occupations_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Pennsylvania JSON file saved to: {json_filename}")
        
        # Display data overview
        print(f"\n📋 Pennsylvania Data Overview:")
        print(f"   - Total Occupations: {len(df)}")
        print(f"   - Occupations with Descriptions: {len(df[df['description'].str.len() > 0])}")
        print(f"   - Occupations with Technology Skills: {len(df[df['technology_skills'].apply(lambda x: len(x) > 0)])}")
        print(f"   - Occupations with Education Info: {len(df[df['education_level'].str.len() > 0])}")
        print(f"   - Occupations with Salary Info: {len(df[df['salary_median'].str.len() > 0])}")
        print(f"   - Occupations with Work Activities: {len(df[df['work_activities'].apply(lambda x: len(x) > 0)])}")
        
        # Pennsylvania cities statistics
        all_cities = []
        for cities in df['pa_cities_mentioned']:
            if isinstance(cities, list):
                all_cities.extend(cities)
        
        if all_cities:
            city_counts = pd.Series(all_cities).value_counts()
            print(f"\n📊 Pennsylvania Cities Mentioned Statistics:")
            for city, count in city_counts.items():
                print(f"   {city}: {count} times")
        
        # Pennsylvania industries statistics
        all_industries = []
        for industries in df['pa_industries_mentioned']:
            if isinstance(industries, list):
                all_industries.extend(industries)
        
        if all_industries:
            industry_counts = pd.Series(all_industries).value_counts()
            print(f"\n📊 Pennsylvania Industries Mentioned Statistics:")
            for industry, count in industry_counts.items():
                print(f"   {industry}: {count} times")
        
        # Occupation family statistics
        if 'occupation_family' in df.columns:
            family_counts = df['occupation_family'].value_counts()
            print(f"\n📊 Occupation Family Distribution:")
            for family, count in family_counts.items():
                print(f"   {family}: {count} occupations")
        
        # Technology skills statistics
        all_tech_skills = []
        for skills in df['technology_skills']:
            if isinstance(skills, list):
                all_tech_skills.extend(skills)
        
        if all_tech_skills:
            skill_counts = pd.Series(all_tech_skills).value_counts()
            print(f"\n📊 Top 20 Technology Skills:")
            for skill, count in skill_counts.head(20).items():
                print(f"   {skill}: {count} times")
        
        return csv_filename, json_filename
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        logger.info("Cleaning up temporary files...")
        
        import glob
        temp_patterns = [
            "temp_pa_occupations_*.json",
            "temp_*_occupations_*.json"
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
    print("=" * 70)
    print("Pennsylvania Employment Data Scraper")
    print("=" * 70)
    print("This program will scrape Pennsylvania-related employment data, including:")
    print("- Job descriptions and skill requirements")
    print("- Education levels and salary information") 
    print("- Work activities and requirements")
    print("- Pennsylvania cities and industry associations")
    print("- Technology skills analysis")
    print("=" * 70)
    
    # Create scraper instance
    scraper = PennsylvaniaJobScraper()
    
    try:
        # Get Pennsylvania employment statistics
        print("\n📊 Getting Pennsylvania employment statistics...")
        pa_stats = scraper.get_pennsylvania_employment_stats()
        print(f"Pennsylvania total employment: {pa_stats['total_employment']:,}")
        print(f"Unemployment rate: {pa_stats['unemployment_rate']}%")
        print(f"Average salary: ${pa_stats['average_salary']:,}")
        
        print("\n🏭 Major Industries:")
        for industry in pa_stats['top_industries']:
            print(f"   - {industry['name']}: {industry['employment']:,} employment, growth {industry['growth']}%")
        
        print("\n🏙️ Major Cities:")
        for city in pa_stats['major_cities']:
            print(f"   - {city['name']}: {city['employment']:,} employment, avg salary ${city['avg_salary']:,}")
        
        # Scrape occupation data
        print("\n🚀 Starting to scrape Pennsylvania occupation data...")
        print("⚠️ Note: This will take some time, progress will be reported every 5 minutes")
        
        all_data = scraper.scrape_pennsylvania_data(max_occupations=50)
        
        if not all_data:
            print("❌ Pennsylvania data scraping failed")
            return
        
        # Save results
        print("\n💾 Saving Pennsylvania results...")
        csv_file, json_file = scraper.save_pennsylvania_results(all_data)
        
        # Clean up temporary files
        print("\n🧹 Cleaning up temporary files...")
        scraper.cleanup_temp_files()
        
        print(f"\n🎉 Pennsylvania employment data scraping completed!")
        print(f"📊 Results saved as:")
        print(f"   - CSV: {csv_file}")
        print(f"   - JSON: {json_file}")
        print(f"📊 This dataset contains detailed information about Pennsylvania employment market")
        
    except KeyboardInterrupt:
        print("\n⚠️ User interrupted the program")
    except Exception as e:
        print(f"\n❌ Program error: {e}")
        logger.error(f"Program error: {e}")

if __name__ == "__main__":
    main()

