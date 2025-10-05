#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Sheets Integration for Pennsylvania Job Data
==================================================

This script integrates job listings data from Google Sheets with the existing
Pennsylvania employment analysis.

Author: Fan Yang (CMU)
Version: 1.0
"""

import pandas as pd
import requests
import os
import json
from datetime import datetime
# import streamlit as st  # Only needed for Streamlit app, not for standalone script

class GoogleSheetsIntegrator:
    """Google Sheets data integration class"""
    
    def __init__(self):
        self.sheets_url = "https://docs.google.com/spreadsheets/d/1kGx-QwGAiwd1zs0PNDuVAbyN1L7V7ezDrdqKXf4Exws/edit?gid=0#gid=0"
        self.csv_export_url = "https://docs.google.com/spreadsheets/d/1kGx-QwGAiwd1zs0PNDuVAbyN1L7V7ezDrdqKXf4Exws/export?format=csv&gid=0"
        
    def download_sheets_data(self):
        """Download data from Google Sheets"""
        try:
            # Download the main sheet
            response = requests.get(self.csv_export_url)
            response.raise_for_status()
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"google_sheets_jobs_{timestamp}.csv"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"Google Sheets data downloaded: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error downloading Google Sheets data: {e}")
            return None
    
    def load_sheets_data(self, filename):
        """Load Google Sheets data into DataFrame"""
        try:
            df = pd.read_csv(filename)
            print(f"Loaded {len(df)} rows from Google Sheets")
            return df
        except Exception as e:
            print(f"Error loading Google Sheets data: {e}")
            return None
    
    def analyze_job_categories(self, df):
        """Analyze job categories in the Google Sheets data"""
        print("\n📊 Job Categories Analysis:")
        print("=" * 50)
        
        # Check for category column
        category_columns = [col for col in df.columns if 'category' in col.lower() or 'type' in col.lower()]
        
        if category_columns:
            for col in category_columns:
                print(f"\n{col} Distribution:")
                category_counts = df[col].value_counts()
                for category, count in category_counts.items():
                    print(f"  - {category}: {count} jobs")
        else:
            print("No category columns found. Available columns:")
            for col in df.columns:
                print(f"  - {col}")
    
    def integrate_with_pa_data(self, sheets_df, pa_df):
        """Integrate Google Sheets data with Pennsylvania O*NET data"""
        print("\n🔗 Integrating Google Sheets data with PA O*NET data...")
        
        # Create integration mapping
        integration_results = []
        
        for idx, job in sheets_df.iterrows():
            job_title = str(job.get('title', '')).lower()
            job_description = str(job.get('description', '')).lower()
            
            # Find matching O*NET occupations
            matches = []
            for _, pa_job in pa_df.iterrows():
                pa_title = str(pa_job.get('title', '')).lower()
                
                # Simple matching logic
                if any(word in pa_title for word in job_title.split() if len(word) > 3):
                    matches.append(pa_job)
            
            if matches:
                # Take the best match (first one for now)
                best_match = matches[0]
                
                integration_results.append({
                    'sheets_job_title': job.get('title', ''),
                    'sheets_description': job.get('description', ''),
                    'onet_title': best_match.get('title', ''),
                    'onet_family': best_match.get('occupation_family', ''),
                    'onet_salary': best_match.get('salary_median_clean', ''),
                    'onet_skills': best_match.get('technology_skills', ''),
                    'match_confidence': 'High' if len(matches) == 1 else 'Medium'
                })
        
        integration_df = pd.DataFrame(integration_results)
        print(f"Successfully integrated {len(integration_df)} jobs")
        
        return integration_df
    
    def save_integration_results(self, integration_df):
        """Save integration results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"integrated_job_data_{timestamp}.csv"
        
        integration_df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Integration results saved: {filename}")
        
        return filename

def main():
    """Main integration function"""
    print("Google Sheets Integration for Pennsylvania Job Data")
    print("=" * 60)
    
    # Initialize integrator
    integrator = GoogleSheetsIntegrator()
    
    # Download Google Sheets data
    print("Downloading Google Sheets data...")
    sheets_file = integrator.download_sheets_data()
    
    if not sheets_file:
        print("Failed to download Google Sheets data")
        return
    
    # Load Google Sheets data
    print("Loading Google Sheets data...")
    sheets_df = integrator.load_sheets_data(sheets_file)
    
    if sheets_df is None:
        print("Failed to load Google Sheets data")
        return
    
    # Analyze job categories
    integrator.analyze_job_categories(sheets_df)
    
    # Load Pennsylvania O*NET data
    print("\nLoading Pennsylvania O*NET data...")
    pa_file = "data/raw_data_project/pennsylvania_all_occupations_20250927_201529.csv"
    
    if not os.path.exists(pa_file):
        print(f"Pennsylvania data file not found: {pa_file}")
        return
    
    pa_df = pd.read_csv(pa_file)
    print(f"Loaded {len(pa_df)} Pennsylvania occupations")
    
    # Integrate data
    integration_df = integrator.integrate_with_pa_data(sheets_df, pa_df)
    
    if len(integration_df) > 0:
        # Save results
        result_file = integrator.save_integration_results(integration_df)
        
        print(f"\nIntegration completed successfully!")
        print(f"Results: {len(integration_df)} jobs integrated")
        print(f"Saved to: {result_file}")
        
        # Show sample results
        print(f"\nSample Integration Results:")
        print(integration_df.head().to_string())
    else:
        print("No jobs could be integrated")

if __name__ == "__main__":
    main()
