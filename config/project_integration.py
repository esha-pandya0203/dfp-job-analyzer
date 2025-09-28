#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pennsylvania Employment Project Integration
==========================================

This script integrates all components of the Pennsylvania employment analysis project:
- O*NET data scraping
- BLS API integration
- Google Sheets data integration
- Data analysis and visualization
- Streamlit dashboard

Author: Fan Yang (CMU)
Version: 1.0
"""

import os
import sys
import subprocess
import pandas as pd
from datetime import datetime

class ProjectIntegrator:
    """Main project integration class"""
    
    def __init__(self):
        self.project_root = os.getcwd()
        self.data_folder = "data/raw_data_project"
        self.output_folder = "output"
        self.modules_folder = "modules"
        
    def check_project_structure(self):
        """Check if project structure is correct"""
        print("Checking project structure...")
        
        required_folders = [self.data_folder, self.modules_folder, "pages", "utils"]
        required_files = [
            "app.py",
            "config/google_sheets_integration.py",
            "scripts/run_dashboard.py"
        ]
        
        missing_items = []
        
        # Check folders
        for folder in required_folders:
            if not os.path.exists(folder):
                missing_items.append(f"Folder: {folder}")
        
        # Check files
        for file in required_files:
            if not os.path.exists(file):
                missing_items.append(f"File: {file}")
        
        if missing_items:
            print("Missing project components:")
            for item in missing_items:
                print(f"   - {item}")
            return False
        
        print("Project structure is correct")
        return True
    
    def run_data_analysis(self):
        """Run the Pennsylvania data analysis"""
        print("\nRunning Pennsylvania data analysis...")
        
        try:
            # Run the analysis script with proper encoding
            result = subprocess.run([
                sys.executable, "utils/analyze_pa_data_fixed.py"
            ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                print("Data analysis completed successfully")
                print("Analysis output:")
                print(result.stdout)
            else:
                print("Data analysis failed:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"Error running data analysis: {e}")
            return False
        
        return True
    
    def integrate_google_sheets(self):
        """Integrate Google Sheets data"""
        print("\nIntegrating Google Sheets data...")
        
        try:
            # Run Google Sheets integration with proper encoding
            result = subprocess.run([
                sys.executable, "config/google_sheets_integration.py"
            ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                print("Google Sheets integration completed")
                print("Integration output:")
                print(result.stdout)
            else:
                print("Google Sheets integration failed:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"Error integrating Google Sheets: {e}")
            return False
        
        return True
    
    def create_project_summary(self):
        """Create a project summary report"""
        print("\nCreating project summary...")
        
        summary = {
            'project_name': 'Pennsylvania Employment Data Analysis',
            'author': 'Fan Yang (CMU)',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'components': {
                'data_scraping': 'O*NET Pennsylvania occupation data',
                'bls_integration': 'Bureau of Labor Statistics API',
                'google_sheets': 'Job listings from Google Sheets',
                'analysis': 'Comprehensive data analysis',
                'visualization': 'Streamlit dashboard'
            },
            'data_sources': [
                'O*NET Online (https://www.onetonline.org/)',
                'Bureau of Labor Statistics API',
                'Google Sheets job listings',
                'Pennsylvania-specific employment data'
            ],
            'outputs': [
                'Pennsylvania occupation dataset',
                'Skills analysis and trends',
                'Salary analysis and projections',
                'Interactive Streamlit dashboard',
                'Integrated job market insights'
            ]
        }
        
        # Save summary to JSON
        summary_file = os.path.join(self.output_folder, "project_summary.json")
        os.makedirs(self.output_folder, exist_ok=True)
        
        import json
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"Project summary saved: {summary_file}")
        return summary
    
    def launch_dashboard(self):
        """Launch the Streamlit dashboard"""
        print("\nLaunching Streamlit dashboard...")
        
        try:
            # Launch dashboard
            subprocess.run([
                sys.executable, "scripts/run_dashboard.py"
            ])
        except KeyboardInterrupt:
            print("\nDashboard stopped by user")
        except Exception as e:
            print(f"Error launching dashboard: {e}")
            return False
        
        return True
    
    def run_full_integration(self):
        """Run the complete project integration"""
        print("Pennsylvania Employment Project Integration")
        print("=" * 60)
        
        # Check project structure
        if not self.check_project_structure():
            print("Project structure check failed")
            return False
        
        # Run data analysis
        if not self.run_data_analysis():
            print("Data analysis failed")
            return False
        
        # Integrate Google Sheets (optional)
        print("\nDo you want to integrate Google Sheets data? (y/n): ", end="")
        integrate_sheets = input().lower().strip() == 'y'
        
        if integrate_sheets:
            if not self.integrate_google_sheets():
                print("Google Sheets integration failed")
                return False
        
        # Create project summary
        summary = self.create_project_summary()
        
        # Launch dashboard
        print("\nDo you want to launch the Streamlit dashboard? (y/n): ", end="")
        launch_dash = input().lower().strip() == 'y'
        
        if launch_dash:
            self.launch_dashboard()
        
        print("\nProject integration completed successfully!")
        print("All components are ready for use")
        
        return True

def main():
    """Main function"""
    integrator = ProjectIntegrator()
    
    try:
        success = integrator.run_full_integration()
        
        if success:
            print("\nPennsylvania Employment Project is ready!")
            print("Check the 'output' folder for analysis results")
            print("Use 'python scripts/run_dashboard.py' to launch the dashboard")
        else:
            print("\nProject integration failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nIntegration stopped by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
