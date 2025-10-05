#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper Manager
===============

A centralized manager for all scraping operations.

Author: Fan Yang (CMU)
Version: 1.0
"""

import os
import time
from .indeed_scraper import IndeedScraper
from .onet_scraper import EnhancedONETScraper
from .skill_matcher import SkillMatcher

class ScraperManager:
    """Centralized scraper manager"""
    
    def __init__(self):
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize scrapers
        self.indeed_scraper = IndeedScraper()
        self.onet_scraper = EnhancedONETScraper()
        self.skill_matcher = SkillMatcher()
        
        # Define job categories to scrape
        self.job_categories = {
            'Software Developer': '15-1252',
            'Data Scientist': '15-2050', 
            'Computer Programmer': '15-1251',
            'Cybersecurity Engineer': '15-1241',
            'Product Manager': '11-3021',
            'Quality Assurance': '15-1253'
        }
    
    def scrape_all_data(self):
        """Run all scraping operations"""
        print("🚀 Starting comprehensive data scraping...")
        print("=" * 50)
        
        results = {
            'onet_data': False,
            'indeed_data': False,
            'skills_matched': False
        }
        
        # 1. Scrape O*NET data
        print("\n📊 Step 1: Scraping O*NET occupation data...")
        try:
            results['onet_data'] = self.onet_scraper.scrape_enhanced_data()
            if results['onet_data']:
                print("✅ O*NET data scraped successfully")
            else:
                print("⚠️ O*NET scraping failed")
        except Exception as e:
            print(f"❌ O*NET scraping error: {e}")
        
        # 2. Scrape Indeed job postings
        print("\n💼 Step 2: Scraping Indeed job postings...")
        indeed_success = 0
        total_jobs = len(self.job_categories)
        
        for job_title, soc_code in self.job_categories.items():
            print(f"\n🔍 Scraping {job_title} jobs...")
            try:
                if self.indeed_scraper.scrape_and_save(job_title, soc_code):
                    indeed_success += 1
                time.sleep(2)  # Be polite to the server
            except Exception as e:
                print(f"❌ Error scraping {job_title}: {e}")
        
        results['indeed_data'] = indeed_success > 0
        print(f"✅ Scraped {indeed_success}/{total_jobs} job categories from Indeed")
        
        # 3. Match skills to job postings
        print("\n🛠️ Step 3: Matching skills to job postings...")
        try:
            results['skills_matched'] = self.skill_matcher.process_all_job_files()
            if results['skills_matched']:
                print("✅ Skills matched successfully")
            else:
                print("⚠️ Skill matching failed")
        except Exception as e:
            print(f"❌ Skill matching error: {e}")
        
        # Summary
        print("\n" + "=" * 50)
        print("📋 Scraping Summary:")
        print(f"  O*NET Data: {'✅' if results['onet_data'] else '❌'}")
        print(f"  Indeed Data: {'✅' if results['indeed_data'] else '❌'}")
        print(f"  Skills Matched: {'✅' if results['skills_matched'] else '❌'}")
        
        success_count = sum(results.values())
        print(f"\n🎯 Overall Success: {success_count}/3 operations completed")
        
        return results
    
    def check_data_freshness(self):
        """Check if data needs updating"""
        print("🔍 Checking data freshness...")
        
        data_files = [
            os.path.join(self.data_dir, "ONET_Data.csv"),
            os.path.join(self.data_dir, "Jobs_with_Matched_Skills.csv")
        ]
        
        needs_update = False
        for file_path in data_files:
            if not os.path.exists(file_path):
                print(f"⚠️ Missing data file: {file_path}")
                needs_update = True
            else:
                # Check file age (simplified - could be more sophisticated)
                file_age = time.time() - os.path.getmtime(file_path)
                if file_age > 7 * 24 * 3600:  # 7 days
                    print(f"⚠️ Data file is old: {file_path}")
                    needs_update = True
        
        if needs_update:
            print("🔄 Data update recommended")
            return True
        else:
            print("✅ Data is fresh")
            return False
    
    def run_smart_update(self):
        """Run update only if needed"""
        if self.check_data_freshness():
            print("\n🚀 Running data update...")
            return self.scrape_all_data()
        else:
            print("ℹ️ Data is up to date, no scraping needed")
            return True
