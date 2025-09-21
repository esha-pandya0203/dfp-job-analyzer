#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Job Market Data Analyzer
========================

Analyze occupation data for skills trends, salary insights, and market analysis.

Author: Fan Yang (CMU)
Version: 1.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

class JobMarketAnalyzer:
    """Job Market Data Analyzer"""
    
    def __init__(self, csv_file='occupations_data.csv', json_file='occupations_data.json'):
        """Initialize analyzer with data files"""
        self.csv_file = csv_file
        self.json_file = json_file
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Load data from CSV and JSON files"""
        try:
            # Load CSV data
            self.df = pd.read_csv(self.csv_file)
            print(f"✅ Loaded {len(self.df)} occupations from CSV")
            
            # Convert string representations of lists back to actual lists
            list_columns = ['skills', 'technology_skills', 'work_activities', 'work_context', 
                          'knowledge_areas', 'abilities', 'work_styles', 'tasks', 'tools_used', 'work_values']
            
            for col in list_columns:
                if col in self.df.columns:
                    self.df[col] = self.df[col].apply(self._parse_list_string)
            
            print(f"📊 Data loaded successfully with {len(self.df.columns)} columns")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            self.df = None
    
    def _parse_list_string(self, value):
        """Parse string representation of list back to actual list"""
        if pd.isna(value) or value == '' or value == '[]':
            return []
        try:
            # Handle string representation of lists
            if isinstance(value, str) and value.startswith('[') and value.endswith(']'):
                # Remove brackets and split by comma, then clean up
                items = value[1:-1].split(',')
                return [item.strip().strip("'\"") for item in items if item.strip()]
            return value
        except:
            return []
    
    def get_data_overview(self):
        """Get overview of the dataset"""
        if self.df is None:
            print("❌ No data loaded")
            return
        
        print("📋 Dataset Overview:")
        print(f"   - Total Occupations: {len(self.df)}")
        print(f"   - Total Columns: {len(self.df.columns)}")
        
        # Data completeness
        print(f"\n📊 Data Completeness:")
        for col in self.df.columns:
            if col in ['skills', 'technology_skills', 'work_activities', 'work_context', 
                      'knowledge_areas', 'abilities', 'work_styles', 'tasks', 'tools_used', 'work_values']:
                non_empty = self.df[col].apply(lambda x: len(x) > 0 if isinstance(x, list) else False).sum()
                print(f"   - {col}: {non_empty}/{len(self.df)} ({non_empty/len(self.df)*100:.1f}%)")
            else:
                non_empty = self.df[col].notna().sum()
                print(f"   - {col}: {non_empty}/{len(self.df)} ({non_empty/len(self.df)*100:.1f}%)")
    
    def analyze_occupation_families(self):
        """Analyze distribution of occupation families"""
        if self.df is None:
            return
        
        print("\n📊 Occupation Family Analysis:")
        family_counts = self.df['occupation_family'].value_counts()
        
        for family, count in family_counts.items():
            percentage = (count / len(self.df)) * 100
            print(f"   - {family}: {count} occupations ({percentage:.1f}%)")
        
        # Create visualization
        plt.figure(figsize=(12, 8))
        family_counts.plot(kind='bar')
        plt.title('Distribution of Occupation Families')
        plt.xlabel('Occupation Family')
        plt.ylabel('Number of Occupations')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
    
    def analyze_technology_skills(self, top_n=20):
        """Analyze most common technology skills"""
        if self.df is None:
            return
        
        print(f"\n💻 Top {top_n} Technology Skills:")
        
        # Flatten all technology skills
        all_skills = []
        for skills in self.df['technology_skills']:
            if isinstance(skills, list):
                all_skills.extend(skills)
        
        skill_counts = Counter(all_skills)
        top_skills = skill_counts.most_common(top_n)
        
        for i, (skill, count) in enumerate(top_skills, 1):
            percentage = (count / len(self.df)) * 100
            print(f"   {i:2d}. {skill}: {count} times ({percentage:.1f}%)")
        
        # Create visualization
        if top_skills:
            skills, counts = zip(*top_skills)
            plt.figure(figsize=(12, 8))
            plt.barh(range(len(skills)), counts)
            plt.yticks(range(len(skills)), skills)
            plt.xlabel('Number of Occupations')
            plt.title(f'Top {top_n} Technology Skills')
            plt.gca().invert_yaxis()
            plt.tight_layout()
            plt.show()
    
    def analyze_salary_by_family(self):
        """Analyze salary distribution by occupation family"""
        if self.df is None:
            return
        
        print("\n💰 Salary Analysis by Occupation Family:")
        
        # Clean salary data
        salary_data = self.df.copy()
        salary_data['salary_numeric'] = salary_data['salary_median'].str.extract(r'(\d+\.?\d*)').astype(float)
        salary_data = salary_data.dropna(subset=['salary_numeric'])
        
        if len(salary_data) == 0:
            print("   No salary data available")
            return
        
        # Group by family and calculate statistics
        family_salary = salary_data.groupby('occupation_family')['salary_numeric'].agg(['mean', 'median', 'count']).round(2)
        family_salary = family_salary.sort_values('median', ascending=False)
        
        print("   Family | Avg Salary | Median Salary | Count")
        print("   " + "-" * 50)
        for family, row in family_salary.iterrows():
            print(f"   {family[:30]:30} | ${row['mean']:8.2f} | ${row['median']:8.2f} | {row['count']:3.0f}")
        
        # Create visualization
        plt.figure(figsize=(14, 8))
        family_salary['median'].plot(kind='bar')
        plt.title('Median Salary by Occupation Family')
        plt.xlabel('Occupation Family')
        plt.ylabel('Median Salary ($)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
    
    def find_high_demand_skills(self, min_occupations=50):
        """Find skills that appear in many occupations"""
        if self.df is None:
            return
        
        print(f"\n🔥 High-Demand Skills (appearing in {min_occupations}+ occupations):")
        
        # Count skills across all occupations
        skill_counts = Counter()
        for skills in self.df['technology_skills']:
            if isinstance(skills, list):
                for skill in skills:
                    skill_counts[skill] += 1
        
        # Filter high-demand skills
        high_demand = {skill: count for skill, count in skill_counts.items() if count >= min_occupations}
        
        if not high_demand:
            print(f"   No skills found appearing in {min_occupations}+ occupations")
            return
        
        sorted_skills = sorted(high_demand.items(), key=lambda x: x[1], reverse=True)
        
        for skill, count in sorted_skills:
            percentage = (count / len(self.df)) * 100
            print(f"   - {skill}: {count} occupations ({percentage:.1f}%)")
    
    def analyze_education_requirements(self):
        """Analyze education requirements across occupations"""
        if self.df is None:
            return
        
        print("\n🎓 Education Requirements Analysis:")
        
        # Extract education keywords
        education_keywords = ['bachelor', 'master', 'phd', 'doctorate', 'associate', 'high school', 'certification']
        education_counts = {keyword: 0 for keyword in education_keywords}
        
        for education in self.df['education_level']:
            if pd.notna(education) and education:
                education_lower = education.lower()
                for keyword in education_keywords:
                    if keyword in education_lower:
                        education_counts[keyword] += 1
        
        total_with_education = self.df['education_level'].notna().sum()
        
        print(f"   Total occupations with education info: {total_with_education}/{len(self.df)}")
        print("\n   Education Level Requirements:")
        for keyword, count in education_counts.items():
            if count > 0:
                percentage = (count / total_with_education) * 100
                print(f"   - {keyword.title()}: {count} occupations ({percentage:.1f}%)")
    
    def search_occupations_by_skill(self, skill_name):
        """Search occupations that require a specific skill"""
        if self.df is None:
            return
        
        print(f"\n🔍 Occupations requiring '{skill_name}':")
        
        matching_occupations = []
        for idx, row in self.df.iterrows():
            if isinstance(row['technology_skills'], list):
                if skill_name.lower() in [s.lower() for s in row['technology_skills']]:
                    matching_occupations.append(row)
        
        if not matching_occupations:
            print(f"   No occupations found requiring '{skill_name}'")
            return
        
        print(f"   Found {len(matching_occupations)} occupations:")
        for occ in matching_occupations[:10]:  # Show top 10
            print(f"   - {occ['title']} ({occ['occupation_family']})")
        
        if len(matching_occupations) > 10:
            print(f"   ... and {len(matching_occupations) - 10} more")
    
    def generate_skills_report(self):
        """Generate comprehensive skills analysis report"""
        if self.df is None:
            return
        
        print("=" * 60)
        print("📊 COMPREHENSIVE SKILLS ANALYSIS REPORT")
        print("=" * 60)
        
        self.get_data_overview()
        self.analyze_occupation_families()
        self.analyze_technology_skills()
        self.find_high_demand_skills()
        self.analyze_education_requirements()
        
        print("\n" + "=" * 60)
        print("✅ Report completed!")

def main():
    """Main function for interactive analysis"""
    print("🔍 Job Market Data Analyzer")
    print("=" * 40)
    
    analyzer = JobMarketAnalyzer()
    
    if analyzer.df is None:
        print("❌ Failed to load data. Please check if the data files exist.")
        return
    
    while True:
        print("\n📋 Available Analysis Options:")
        print("1. Data Overview")
        print("2. Occupation Family Analysis")
        print("3. Technology Skills Analysis")
        print("4. Salary Analysis")
        print("5. High-Demand Skills")
        print("6. Education Requirements")
        print("7. Search Occupations by Skill")
        print("8. Generate Full Report")
        print("9. Exit")
        
        choice = input("\nSelect an option (1-9): ").strip()
        
        if choice == '1':
            analyzer.get_data_overview()
        elif choice == '2':
            analyzer.analyze_occupation_families()
        elif choice == '3':
            analyzer.analyze_technology_skills()
        elif choice == '4':
            analyzer.analyze_salary_by_family()
        elif choice == '5':
            min_occ = input("Minimum number of occupations (default 50): ").strip()
            min_occ = int(min_occ) if min_occ.isdigit() else 50
            analyzer.find_high_demand_skills(min_occ)
        elif choice == '6':
            analyzer.analyze_education_requirements()
        elif choice == '7':
            skill = input("Enter skill name to search: ").strip()
            if skill:
                analyzer.search_occupations_by_skill(skill)
        elif choice == '8':
            analyzer.generate_skills_report()
        elif choice == '9':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()
