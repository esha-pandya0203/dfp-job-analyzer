#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced O*NET Scraper V2 - Complete Data Extraction
====================================================

This enhanced scraper accesses detailed sub-pages for each occupation
to extract comprehensive information including skills, education, work context, etc.

Author: Fan Yang (CMU)
Version: 2.0
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
import glob
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedONETScraper:
    """Enhanced O*NET Scraper - Complete Data Extraction"""
    
    def __init__(self, bls_dict=None):
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
        
        # BLS occupation code dictionary - for filtering specific occupations
        self.bls_dict = bls_dict or {
            '15-1251': ['AI', 'ML', 'Artificial Intelligence', 'Machine Learning', 'Generative AI', 'Gen AI', 'LLM', 'Software Engineer with Poly Mid', 'Cloud', 'IT Security', 'IT', 'Support Technician', 'IT Support', 'Product Support Engineer', 'Lead', 'Technical Support', 'Windows Engineer', 'Tech Leader', 'CIO', 'Technology Officer', 'Azure', 'AWS', 'Technology', 'Reliability Engineer', 'Customer Success Manager', 'Monitoring Center Analyst', 'Customer Success', 'SDSA', 'Site Reliability Engineer', 'CCaaS', 'IAM', 'GEN AI Architect', 'Technoogy & Innovation', 'Platform Engineer'], 
            '15-1252': ['DevOps', 'Release Manager', 'PaaS Lead', 'Platorm Infrastructure Engineer', 'RHEL Engineer', 'RHEL', 'Experienced Software Engineer', 'Software', 'Developer', 'Frontend engineer', 'Backend Engineer', 'Full Stack', 'Frontend', 'Backend', 'React'], 
            '15-1253': ['Operations', 'General Manager', 'Project Coordinator', 'Administrative Business Partner', 'Logistics', 'Customer Experience Specialist', 'Brand Manager', 'Plant Manager', 'Customer Success', 'Demand Planner', 'Workforce Management', 'Operational', 'Supply Chain', 'Coordinator', 'Extruder Area Manager', 'Administrative Assistant', 'Operating', 'Commodities', 'People, Culture, & Performance', 'Executive Assistant', 'Regional Manager', 'Assistant', 'Concierge', 'Learning & Development', 'Marketing', 'Executive', 'Customer Success', 'VP', 'Vice President', 'Field Deployment Lead', 'Warehouse Lead', 'Regional Sales', 'Store Manager', 'HR', 'Retail', 'Recruiter', 'QA', 'Quality Assurance', 'Tester', 'Quality Control'], 
            '15-2050': ['Data', 'Business Intelligence Analyst', 'Analytics', 'Analyst', 'PowerBI Developer', 'Quantitative', 'Applied Scientist', 'Machine Learning', 'Research Scientist', 'Decision Science', 'Scientist', 'AI', 'ML', 'Gen AI'], 
            '11-3021': ['Product', 'Wealth Management Analyst', ' Creative Strategist', 'UX', 'UI', 'Solutions', 'Technical Product Manager'], 
            '15-1241': ['Information Security', 'SOC', 'Cybersecurity', 'Cyber', 'Security', 'Compliance', 'Information System', 'Help Desk Support', 'Engineer, Data Center', 'Security Risk Analyst', 'IT', 'IT Support', 'Privacy', 'Incident Response', 'Data Center', 'Strategy', 'Vulnerability', 'Network', 'Threat Analyst', 'Technology and Innovation', 'Security Operations', 'Counterintelligence', 'Risk', 'Internal Audit', 'Incident', 'Threat', 'Anti-Money Laundering', 'Comply-to-Connect & Endpoint Policy Analyst'] 
        }
        
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
            # Extract code from URL like /link/summary/15-2011.00
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
            # Extract first two digits from code like 15-2011.00
            family_id = int(code.split('-')[0])
            return self.occupation_families.get(family_id, "Unknown")
        except:
            return "Unknown"
    
    def should_scrape_occupation(self, title, code):
        """Check if occupation should be scraped based on BLS dictionary"""
        if not self.bls_dict:
            return True  # If no BLS dict provided, scrape all
        
        # Check if the occupation code matches any BLS code
        for bls_code, keywords in self.bls_dict.items():
            # Check if the O*NET code matches the BLS code pattern
            if code and code.startswith(bls_code):
                return True
            
            # Check if any keyword matches the title
            title_lower = title.lower()
            for keyword in keywords:
                if keyword.lower() in title_lower:
                    return True
        
        return False
    
    def get_all_occupation_links(self):
        """Get all occupation links with family information, filtered by BLS dictionary"""
        logger.info("Starting to get occupation links filtered by BLS dictionary...")
        all_links = {}
        
        for family_id, family_name in self.occupation_families.items():
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
                            # Extract occupation code from URL
                            code = self.get_occupation_code_from_url(full_url)
                            
                            # Check if this occupation should be scraped
                            if self.should_scrape_occupation(title, code):
                                family_links[title] = {
                                    'url': full_url,
                                    'family': family_name,
                                    'family_id': family_id,
                                    'code': code
                                }
                                logger.info(f"Selected occupation: {title} (Code: {code})")
                            else:
                                logger.debug(f"Skipped occupation: {title} (Code: {code})")
                    break
            
            all_links.update(family_links)
            logger.info(f"{family_name}: Found {len(family_links)} matching occupations")
            
            # Add delay to avoid being blocked
            time.sleep(2)
        
        logger.info(f"Total found {len(all_links)} occupation links matching BLS criteria")
        return all_links
    
    
    
    
    
    
    def extract_abilities_from_page(self, soup):
        """Extract abilities"""
        abilities = []
        try:
            # Look for abilities
            ability_elements = soup.find_all(['li', 'td', 'span'])
            for element in ability_elements:
                text = element.get_text(strip=True)
                if text and len(text) > 5 and len(text) < 100:
                    # Check if it looks like an ability
                    if any(keyword in text.lower() for keyword in ['ability', 'skill', 'capability', 'proficiency', 'competence']):
                        abilities.append(text)
        except Exception as e:
            logger.warning(f"Error extracting abilities: {e}")
        
        return abilities[:10]  # Limit to top 10
    
    
    
    
    
    
    def extract_comprehensive_data(self, title, url, family_info):
        """Extract essential data from occupation page"""
        logger.info(f"Extracting essential data for: {title}")
        
        # Initialize simplified data structure
        data = {
            'title': title,
            'occupation_code': self.get_occupation_code_from_url(url),
            'occupation_family': family_info['family'],
            'occupation_family_id': family_info['family_id'],
            'description': '',
            'technology_skills': [],
            'salary_median': '',
            'abilities': [],
            'url': url
        }
        
        # Get main summary page
        soup = self.get_page(url)
        if not soup:
            logger.warning(f"Unable to get main page for {title}")
            return data
        
        try:
            # Extract basic information from main page
            page_text = soup.get_text()
            
            # Extract description
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 100 and any(keyword in text.lower() for keyword in ['analyze', 'develop', 'design', 'manage', 'implement', 'create', 'provide']):
                    data['description'] = text
                    break
            
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
            
            # Extract only essential data
            data['abilities'] = self.extract_abilities_from_page(soup)
            
            # Extract technology skills
            page_text_lower = page_text.lower()
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
            
        except Exception as e:
            logger.error(f"Error extracting comprehensive data for {title}: {e}")
        
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
        
        print(f"\nProgress Report - {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Progress: {current}/{total} ({progress_percent:.1f}%)")
        print(f"   Success: {success_count}, Failed: {failed_count}")
        print(f"   Elapsed Time: {elapsed_time}")
        print(f"   Estimated Remaining: {estimated_remaining}")
        print(f"   Success Rate: {(success_count/(success_count+failed_count)*100):.1f}%" if (success_count+failed_count) > 0 else "0%")
    
    def scrape_all_occupations_enhanced(self):
        """Scrape all occupation data with enhanced extraction"""
        logger.info("Starting enhanced scraping of all O*NET occupation data...")
        
        # Get all occupation links
        all_links = self.get_all_occupation_links()
        
        if not all_links:
            logger.error("Unable to get occupation links")
            return []
        
        logger.info(f"Starting to scrape {len(all_links)} occupations with enhanced extraction...")
        
        all_data = []
        failed_count = 0
        
        for i, (title, link_info) in enumerate(all_links.items(), 1):
            try:
                data = self.extract_comprehensive_data(title, link_info['url'], link_info)
                if data:
                    all_data.append(data)
                    logger.info(f"Successfully extracted data for: {title}")
                else:
                    failed_count += 1
                    logger.warning(f"Failed to extract data for: {title}")
            except Exception as e:
                failed_count += 1
                logger.error(f"Error processing {title}: {e}")
            
            # Add delay to avoid being blocked
            time.sleep(3)  # Increased delay for more thorough scraping
            
            # Report progress every 10 minutes
            if self.should_report_progress():
                self.report_progress(i, len(all_links), len(all_data), failed_count)
            
            # Save intermediate results every 25 occupations
            if i % 25 == 0:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_file = f"temp_enhanced_occupations_{timestamp}.json"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=2)
                logger.info(f"Intermediate results saved to: {temp_file}")
        
        # Final progress report
        self.report_progress(len(all_links), len(all_links), len(all_data), failed_count)
        
        logger.info(f"Enhanced O*NET data scraping completed, obtained {len(all_data)} occupation data, failed {failed_count}")
        return all_data
    
    def save_enhanced_results(self, all_data):
        """Save enhanced results"""
        logger.info("Saving enhanced results...")
        
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Create data directory if it doesn't exist
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        
        # Export to CSV with fixed filename
        csv_filename = os.path.join(data_dir, "ONET_Data.csv")
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        logger.info(f"ONET Data CSV file saved to: {csv_filename}")
        
        # Export to JSON with fixed filename
        json_filename = os.path.join(data_dir, "ONET_Data.json")
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        logger.info(f"ONET Data JSON file saved to: {json_filename}")
        
        # Display simplified data overview
        print(f"\nSimplified Data Overview:")
        print(f"   - Total Occupations: {len(df)}")
        print(f"   - Occupations with Descriptions: {len(df[df['description'].str.len() > 0])}")
        print(f"   - Occupations with Technology Skills: {len(df[df['technology_skills'].apply(lambda x: len(x) > 0)])}")
        print(f"   - Occupations with Salary Info: {len(df[df['salary_median'].str.len() > 0])}")
        print(f"   - Occupations with Abilities: {len(df[df['abilities'].apply(lambda x: len(x) > 0)])}")
        
        # Occupation family statistics
        if 'occupation_family' in df.columns:
            family_counts = df['occupation_family'].value_counts()
            print(f"\nOccupation Family Distribution:")
            for family, count in family_counts.items():
                print(f"   {family}: {count} occupations")
        
        # Technology skills statistics
        all_tech_skills = []
        for skills in df['technology_skills']:
            if isinstance(skills, list):
                all_tech_skills.extend(skills)
        
        if all_tech_skills:
            skill_counts = pd.Series(all_tech_skills).value_counts()
            print(f"\nTop 20 Technology Skills:")
            for skill, count in skill_counts.head(20).items():
                print(f"   {skill}: {count} times")
        
        return csv_filename, json_filename
    
    def get_latest_data_file(self):
        """Get the latest data files"""
        data_dir = Path("data")
        if not data_dir.exists():
            return None, None
        
        # Check for fixed filename ONET_Data files
        csv_file = data_dir / "ONET_Data.csv"
        json_file = data_dir / "ONET_Data.json"
        
        if csv_file.exists() and json_file.exists():
            return csv_file, json_file
        
        return None, None
    
    def load_existing_data(self):
        """Load existing data"""
        csv_file, json_file = self.get_latest_data_file()
        if csv_file is None:
            return pd.DataFrame(), []
        
        try:
            # Load CSV data
            df = pd.read_csv(csv_file)
            logger.info(f"Loaded existing data from {csv_file}: {len(df)} occupations")
            
            # Load JSON data
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            return df, json_data
        except Exception as e:
            logger.error(f"Failed to load existing data: {e}")
            return pd.DataFrame(), []
    
    def check_for_updates(self, existing_df):
        """Check if there are new occupation data updates on the website"""
        try:
            # Get all occupation links
            all_links = self.get_all_occupation_links()
            
            # Extract existing occupation codes
            existing_codes = set(existing_df['occupation_code'].tolist())
            
            # Check for new occupation codes
            new_codes = set()
            for title, link_info in all_links.items():
                code = link_info.get('code')
                if code and code not in existing_codes:
                    new_codes.add(code)
            
            logger.info(f"Found {len(new_codes)} new occupations: {list(new_codes)[:5]}...")
            return list(new_codes)
            
        except Exception as e:
            logger.error(f"Failed to check for updates: {e}")
            return []
    
    def scrape_incremental_updates(self, new_codes):
        """Incrementally scrape new occupation data"""
        if not new_codes:
            logger.info("No new occupations to scrape")
            return []
        
        logger.info(f"Starting incremental scraping for {len(new_codes)} new occupations")
        
        # Get all occupation links
        all_links = self.get_all_occupation_links()
        
        # Filter links for new occupations
        new_links = {}
        for title, link_info in all_links.items():
            code = link_info.get('code')
            if code in new_codes:
                new_links[title] = link_info
        
        logger.info(f"Found {len(new_links)} matching links for new occupations")
        
        # Scrape new occupation data
        new_data = []
        for i, (title, link_info) in enumerate(new_links.items(), 1):
            try:
                logger.info(f"Scraping new occupation {i}/{len(new_links)}: {title}")
                
                # Extract data
                data = self.extract_comprehensive_data(title, link_info['url'], link_info)
                if data:
                    new_data.append(data)
                
                # Add delay
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to scrape {title}: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(new_data)} new occupations")
        return new_data
    
    def merge_data(self, existing_data, new_data):
        """Merge old and new data"""
        if not new_data:
            return existing_data
        
        # Convert to DataFrame
        new_df = pd.DataFrame(new_data)
        
        if existing_data.empty:
            return new_df
        
        # Merge data
        merged_df = pd.concat([existing_data, new_df], ignore_index=True)
        
        # Remove duplicates (based on occupation_code)
        merged_df = merged_df.drop_duplicates(subset=['occupation_code'], keep='last')
        
        logger.info(f"Merged data: {len(existing_data)} + {len(new_data)} = {len(merged_df)} occupations")
        return merged_df
    
    def run_incremental_update(self):
        """Run incremental update"""
        logger.info("Starting incremental update check...")
        
        # Load existing data
        existing_df, existing_json = self.load_existing_data()
        
        if existing_df.empty:
            logger.info("No existing data found, running full scrape...")
            return self.scrape_all_occupations_enhanced()
        
        # Check for updates
        new_codes = self.check_for_updates(existing_df)
        
        if not new_codes:
            logger.info("No updates found")
            return existing_json
        
        # Scrape new data
        new_data = self.scrape_incremental_updates(new_codes)
        
        if not new_data:
            logger.info("No new data scraped")
            return existing_json
        
        # Merge data
        merged_df = self.merge_data(existing_df, new_data)
        
        # Save updated data
        all_data = merged_df.to_dict('records')
        self.save_enhanced_results(all_data)
        
        logger.info(f"Incremental update completed: added {len(new_data)} new occupations")
        return all_data
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        logger.info("Cleaning up temporary files...")
        
        # Delete temporary files
        temp_patterns = [
            "temp_enhanced_occupations_*.json",
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
    print("Simplified O*NET Scraper - BLS Filtered Data Extraction")
    print("=" * 70)
    print("This simplified scraper will extract essential data for specific BLS occupations:")
    print("- Technology skills requirements")
    print("- Job descriptions")
    print("- Salary information")
    print("- Abilities")
    print("- Occupation family categories")
    print("=" * 70)
    
    # Define BLS dictionary for filtering
    bls_dict = {
        '15-1251': ['AI', 'ML', 'Artificial Intelligence', 'Machine Learning', 'Generative AI', 'Gen AI', 'LLM', 'Software Engineer with Poly Mid', 'Cloud', 'IT Security', 'IT', 'Support Technician', 'IT Support', 'Product Support Engineer', 'Lead', 'Technical Support', 'Windows Engineer', 'Tech Leader', 'CIO', 'Technology Officer', 'Azure', 'AWS', 'Technology', 'Reliability Engineer', 'Customer Success Manager', 'Monitoring Center Analyst', 'Customer Success', 'SDSA', 'Site Reliability Engineer', 'CCaaS', 'IAM', 'GEN AI Architect', 'Technoogy & Innovation', 'Platform Engineer'], 
        '15-1252': ['DevOps', 'Release Manager', 'PaaS Lead', 'Platorm Infrastructure Engineer', 'RHEL Engineer', 'RHEL', 'Experienced Software Engineer', 'Software', 'Developer', 'Frontend engineer', 'Backend Engineer', 'Full Stack', 'Frontend', 'Backend', 'React'], 
        '15-1253': ['Operations', 'General Manager', 'Project Coordinator', 'Administrative Business Partner', 'Logistics', 'Customer Experience Specialist', 'Brand Manager', 'Plant Manager', 'Customer Success', 'Demand Planner', 'Workforce Management', 'Operational', 'Supply Chain', 'Coordinator', 'Extruder Area Manager', 'Administrative Assistant', 'Operating', 'Commodities', 'People, Culture, & Performance', 'Executive Assistant', 'Regional Manager', 'Assistant', 'Concierge', 'Learning & Development', 'Marketing', 'Executive', 'Customer Success', 'VP', 'Vice President', 'Field Deployment Lead', 'Warehouse Lead', 'Regional Sales', 'Store Manager', 'HR', 'Retail', 'Recruiter', 'QA', 'Quality Assurance', 'Tester', 'Quality Control'], 
        '15-2050': ['Data', 'Business Intelligence Analyst', 'Analytics', 'Analyst', 'PowerBI Developer', 'Quantitative', 'Applied Scientist', 'Machine Learning', 'Research Scientist', 'Decision Science', 'Scientist', 'AI', 'ML', 'Gen AI'], 
        '11-3021': ['Product', 'Wealth Management Analyst', ' Creative Strategist', 'UX', 'UI', 'Solutions', 'Technical Product Manager'], 
        '15-1241': ['Information Security', 'SOC', 'Cybersecurity', 'Cyber', 'Security', 'Compliance', 'Information System', 'Help Desk Support', 'Engineer, Data Center', 'Security Risk Analyst', 'IT', 'IT Support', 'Privacy', 'Incident Response', 'Data Center', 'Strategy', 'Vulnerability', 'Network', 'Threat Analyst', 'Technology and Innovation', 'Security Operations', 'Counterintelligence', 'Risk', 'Internal Audit', 'Incident', 'Threat', 'Anti-Money Laundering', 'Comply-to-Connect & Endpoint Policy Analyst'] 
    }
    
    # Create enhanced scraper instance with BLS dictionary
    scraper = EnhancedONETScraper(bls_dict=bls_dict)
    
    try:
        # Scrape filtered data with simplified extraction
        print("\nStarting simplified scraping of BLS-filtered occupation data...")
        print("Note: This will extract essential data for occupations matching the specified BLS codes and keywords")
        print("Progress will be reported every 10 minutes")
        
        all_data = scraper.scrape_all_occupations_enhanced()
        
        if not all_data:
            print("Simplified scraping failed")
            return
        
        # Save simplified results
        print("\nSaving simplified results...")
        csv_file, json_file = scraper.save_enhanced_results(all_data)
        
        # Clean up temporary files
        print("\nCleaning up temporary files...")
        scraper.cleanup_temp_files()
        
        print(f"\nBLS-filtered occupation data scraping completed!")
        print(f"Simplified results saved as:")
        print(f"   - CSV: {csv_file}")
        print(f"   - JSON: {json_file}")
        print(f"This dataset includes essential information for BLS-specified occupations")
        
    except KeyboardInterrupt:
        print("\nUser interrupted the program")
    except Exception as e:
        print(f"\nProgram error: {e}")
        logger.error(f"Program error: {e}")

if __name__ == "__main__":
    main()
