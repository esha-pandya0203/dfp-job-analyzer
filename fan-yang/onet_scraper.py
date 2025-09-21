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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedONETScraper:
    """Enhanced O*NET Scraper - Complete Data Extraction"""
    
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
    
    def get_all_occupation_links(self):
        """Get all occupation links with family information"""
        logger.info("Starting to get all occupation links...")
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
        
        logger.info(f"Total found {len(all_links)} occupation links")
        return all_links
    
    def extract_skills_from_page(self, soup):
        """Extract skills from skills page"""
        skills = []
        try:
            # Look for skills in various formats
            skill_elements = soup.find_all(['li', 'td', 'span'], class_=re.compile(r'skill|ability'))
            for element in skill_elements:
                text = element.get_text(strip=True)
                if text and len(text) > 3 and len(text) < 100:
                    skills.append(text)
            
            # Also look for skills in tables
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    for cell in cells:
                        text = cell.get_text(strip=True)
                        if text and len(text) > 3 and len(text) < 100:
                            skills.append(text)
        except Exception as e:
            logger.warning(f"Error extracting skills: {e}")
        
        return list(set(skills))  # Remove duplicates
    
    def extract_education_from_page(self, soup):
        """Extract education requirements"""
        education = ""
        try:
            # Look for education-related text
            page_text = soup.get_text().lower()
            
            education_keywords = [
                'bachelor', 'master', 'phd', 'doctorate', 'associate', 'high school',
                'college', 'university', 'degree', 'certification', 'diploma'
            ]
            
            for keyword in education_keywords:
                if keyword in page_text:
                    # Find the sentence containing the keyword
                    sentences = soup.get_text().split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower() and len(sentence.strip()) > 10:
                            education = sentence.strip()
                            break
                    if education:
                        break
        except Exception as e:
            logger.warning(f"Error extracting education: {e}")
        
        return education
    
    def extract_work_activities_from_page(self, soup):
        """Extract work activities"""
        activities = []
        try:
            # Look for work activities in various formats
            activity_elements = soup.find_all(['li', 'p', 'td'])
            for element in activity_elements:
                text = element.get_text(strip=True)
                if text and len(text) > 20 and len(text) < 200:
                    # Check if it looks like a work activity
                    if any(keyword in text.lower() for keyword in ['analyze', 'develop', 'design', 'manage', 'implement', 'create', 'provide', 'maintain', 'operate', 'supervise']):
                        activities.append(text)
        except Exception as e:
            logger.warning(f"Error extracting work activities: {e}")
        
        return activities[:10]  # Limit to top 10
    
    def extract_work_context_from_page(self, soup):
        """Extract work context information"""
        context = []
        try:
            # Look for work context information
            context_keywords = ['office', 'field', 'laboratory', 'factory', 'remote', 'travel', 'team', 'independent', 'outdoor', 'indoor']
            
            page_text = soup.get_text()
            for keyword in context_keywords:
                if keyword in page_text.lower():
                    # Find sentences containing the keyword
                    sentences = page_text.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower() and len(sentence.strip()) > 10:
                            context.append(sentence.strip())
                            break
        except Exception as e:
            logger.warning(f"Error extracting work context: {e}")
        
        return context[:5]  # Limit to top 5
    
    def extract_knowledge_areas_from_page(self, soup):
        """Extract knowledge areas"""
        knowledge = []
        try:
            # Look for knowledge-related content
            knowledge_elements = soup.find_all(['li', 'td', 'span'])
            for element in knowledge_elements:
                text = element.get_text(strip=True)
                if text and len(text) > 5 and len(text) < 100:
                    # Check if it looks like a knowledge area
                    if any(keyword in text.lower() for keyword in ['mathematics', 'science', 'engineering', 'technology', 'business', 'law', 'medicine', 'education', 'psychology']):
                        knowledge.append(text)
        except Exception as e:
            logger.warning(f"Error extracting knowledge areas: {e}")
        
        return list(set(knowledge))[:10]  # Remove duplicates and limit
    
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
    
    def extract_work_styles_from_page(self, soup):
        """Extract work styles"""
        styles = []
        try:
            # Look for work styles
            style_keywords = ['detail', 'integrity', 'dependability', 'cooperation', 'initiative', 'leadership', 'stress', 'adaptability', 'achievement', 'independence']
            
            page_text = soup.get_text()
            for keyword in style_keywords:
                if keyword in page_text.lower():
                    sentences = page_text.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower() and len(sentence.strip()) > 10:
                            styles.append(sentence.strip())
                            break
        except Exception as e:
            logger.warning(f"Error extracting work styles: {e}")
        
        return styles[:5]  # Limit to top 5
    
    def extract_tasks_from_page(self, soup):
        """Extract tasks"""
        tasks = []
        try:
            # Look for tasks
            task_elements = soup.find_all(['li', 'p', 'td'])
            for element in task_elements:
                text = element.get_text(strip=True)
                if text and len(text) > 15 and len(text) < 200:
                    # Check if it looks like a task
                    if any(keyword in text.lower() for keyword in ['task', 'duty', 'responsibility', 'function', 'perform', 'execute', 'complete']):
                        tasks.append(text)
        except Exception as e:
            logger.warning(f"Error extracting tasks: {e}")
        
        return tasks[:10]  # Limit to top 10
    
    def extract_tools_from_page(self, soup):
        """Extract tools and technology"""
        tools = []
        try:
            # Look for tools and technology
            tool_elements = soup.find_all(['li', 'td', 'span'])
            for element in tool_elements:
                text = element.get_text(strip=True)
                if text and len(text) > 3 and len(text) < 100:
                    # Check if it looks like a tool or technology
                    if any(keyword in text.lower() for keyword in ['software', 'hardware', 'tool', 'equipment', 'system', 'platform', 'application', 'database', 'server']):
                        tools.append(text)
        except Exception as e:
            logger.warning(f"Error extracting tools: {e}")
        
        return list(set(tools))[:15]  # Remove duplicates and limit
    
    def extract_work_values_from_page(self, soup):
        """Extract work values"""
        values = []
        try:
            # Look for work values
            value_keywords = ['achievement', 'recognition', 'relationships', 'support', 'working conditions', 'independence', 'variety', 'compensation', 'advancement', 'security']
            
            page_text = soup.get_text()
            for keyword in value_keywords:
                if keyword in page_text.lower():
                    sentences = page_text.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower() and len(sentence.strip()) > 10:
                            values.append(sentence.strip())
                            break
        except Exception as e:
            logger.warning(f"Error extracting work values: {e}")
        
        return values[:5]  # Limit to top 5
    
    def extract_job_growth_from_page(self, soup):
        """Extract job growth information"""
        growth = ""
        try:
            # Look for job growth information
            growth_keywords = ['growth', 'increase', 'decrease', 'decline', 'projected', 'outlook', 'employment', 'demand']
            
            page_text = soup.get_text()
            for keyword in growth_keywords:
                if keyword in page_text.lower():
                    sentences = page_text.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower() and len(sentence.strip()) > 10:
                            growth = sentence.strip()
                            break
                    if growth:
                        break
        except Exception as e:
            logger.warning(f"Error extracting job growth: {e}")
        
        return growth
    
    def extract_comprehensive_data(self, title, url, family_info):
        """Extract comprehensive data from occupation page and sub-pages"""
        logger.info(f"Extracting comprehensive data for: {title}")
        
        # Initialize data structure
        data = {
            'title': title,
            'occupation_code': self.get_occupation_code_from_url(url),
            'occupation_family': family_info['family'],
            'occupation_family_id': family_info['family_id'],
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
            
            # Extract basic skills and activities from main page
            data['skills'] = self.extract_skills_from_page(soup)
            data['work_activities'] = self.extract_work_activities_from_page(soup)
            data['education_level'] = self.extract_education_from_page(soup)
            data['job_growth'] = self.extract_job_growth_from_page(soup)
            data['work_context'] = self.extract_work_context_from_page(soup)
            data['knowledge_areas'] = self.extract_knowledge_areas_from_page(soup)
            data['abilities'] = self.extract_abilities_from_page(soup)
            data['work_styles'] = self.extract_work_styles_from_page(soup)
            data['tasks'] = self.extract_tasks_from_page(soup)
            data['tools_used'] = self.extract_tools_from_page(soup)
            data['work_values'] = self.extract_work_values_from_page(soup)
            
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
        
        print(f"\n📊 Progress Report - {datetime.now().strftime('%H:%M:%S')}")
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
        
        # Export to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"enhanced_occupations_complete_{timestamp}.csv"
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        logger.info(f"Enhanced CSV file saved to: {csv_filename}")
        
        # Export to JSON
        json_filename = f"enhanced_occupations_complete_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Enhanced JSON file saved to: {json_filename}")
        
        # Display enhanced data overview
        print(f"\n📋 Enhanced Data Overview:")
        print(f"   - Total Occupations: {len(df)}")
        print(f"   - Occupations with Descriptions: {len(df[df['description'].str.len() > 0])}")
        print(f"   - Occupations with Skills: {len(df[df['skills'].apply(lambda x: len(x) > 0)])}")
        print(f"   - Occupations with Technology Skills: {len(df[df['technology_skills'].apply(lambda x: len(x) > 0)])}")
        print(f"   - Occupations with Education Info: {len(df[df['education_level'].str.len() > 0])}")
        print(f"   - Occupations with Salary Info: {len(df[df['salary_median'].str.len() > 0])}")
        print(f"   - Occupations with Job Growth Info: {len(df[df['job_growth'].str.len() > 0])}")
        print(f"   - Occupations with Work Activities: {len(df[df['work_activities'].apply(lambda x: len(x) > 0)])}")
        print(f"   - Occupations with Work Context: {len(df[df['work_context'].apply(lambda x: len(x) > 0)])}")
        print(f"   - Occupations with Knowledge Areas: {len(df[df['knowledge_areas'].apply(lambda x: len(x) > 0)])}")
        print(f"   - Occupations with Abilities: {len(df[df['abilities'].apply(lambda x: len(x) > 0)])}")
        print(f"   - Occupations with Work Styles: {len(df[df['work_styles'].apply(lambda x: len(x) > 0)])}")
        print(f"   - Occupations with Tasks: {len(df[df['tasks'].apply(lambda x: len(x) > 0)])}")
        print(f"   - Occupations with Tools: {len(df[df['tools_used'].apply(lambda x: len(x) > 0)])}")
        print(f"   - Occupations with Work Values: {len(df[df['work_values'].apply(lambda x: len(x) > 0)])}")
        
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
    print("Enhanced O*NET Scraper V2 - Complete Data Extraction")
    print("=" * 70)
    print("This enhanced scraper will extract comprehensive data including:")
    print("- Skills and technology requirements")
    print("- Education levels and requirements") 
    print("- Work activities and context")
    print("- Knowledge areas and abilities")
    print("- Work styles and values")
    print("- Tasks and tools used")
    print("- Occupation family categories")
    print("=" * 70)
    
    # Create enhanced scraper instance
    scraper = EnhancedONETScraper()
    
    try:
        # Scrape all data with enhanced extraction
        print("\n🚀 Starting enhanced scraping of all occupation data...")
        print("⚠️ Note: This will take significantly longer due to comprehensive data extraction")
        print("⚠️ Progress will be reported every 10 minutes")
        
        all_data = scraper.scrape_all_occupations_enhanced()
        
        if not all_data:
            print("❌ Enhanced scraping failed")
            return
        
        # Save enhanced results
        print("\n💾 Saving enhanced results...")
        csv_file, json_file = scraper.save_enhanced_results(all_data)
        
        # Clean up temporary files
        print("\n🧹 Cleaning up temporary files...")
        scraper.cleanup_temp_files()
        
        print(f"\n🎉 Enhanced occupation data scraping completed!")
        print(f"📊 Enhanced results saved as:")
        print(f"   - CSV: {csv_file}")
        print(f"   - JSON: {json_file}")
        print(f"📊 This enhanced dataset includes comprehensive information for better analysis")
        
    except KeyboardInterrupt:
        print("\n⚠️ User interrupted the program")
    except Exception as e:
        print(f"\n❌ Program error: {e}")
        logger.error(f"Program error: {e}")

if __name__ == "__main__":
    main()
