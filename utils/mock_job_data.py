#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock Job Data Generator
======================

This module generates mock job data for testing purposes when
the actual Google Sheets data is not accessible.

Author: Project Team
Version: 1.0
"""

import pandas as pd
import random
from datetime import datetime

def generate_mock_job_data(num_jobs=100):
    """Generate mock job data for testing"""
    
    # Job titles based on the project requirements
    job_titles = [
        "Software Developer", "Data Analyst", "Data Scientist", "Data Engineer",
        "Cybersecurity Engineer", "Cloud Engineer", "DevOps Engineer", "AI/ML Engineer",
        "Machine Learning Engineer", "Technical Product Manager", "QA Engineer",
        "Software Tester", "Network Engineer", "IT Support Specialist",
        "Full Stack Developer", "Frontend Developer", "Backend Developer",
        "Mobile Developer", "Python Developer", "Java Developer", "React Developer",
        "Angular Developer", "Node.js Developer", "C# Developer", "Security Analyst",
        "Information Security Engineer", "Cloud Solutions Engineer", "AWS Engineer",
        "Azure Engineer", "Google Cloud Engineer", "Penetration Tester",
        "Ethical Hacker", "Security Consultant", "System Administrator",
        "Database Administrator", "Business Intelligence Analyst", "Analytics Engineer",
        "Data Architect", "ETL Developer", "Big Data Engineer", "Quantitative Analyst"
    ]
    
    # Companies
    companies = [
        "Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix", "Uber", "Airbnb",
        "Tesla", "SpaceX", "IBM", "Oracle", "Salesforce", "Adobe", "Intel", "NVIDIA",
        "Cisco", "VMware", "Red Hat", "GitHub", "GitLab", "Atlassian", "Slack",
        "Zoom", "Shopify", "Square", "PayPal", "Stripe", "Twilio", "MongoDB",
        "Redis", "Elastic", "Docker", "Kubernetes", "HashiCorp", "Databricks",
        "Snowflake", "Palantir", "Tableau", "PowerBI", "Splunk", "New Relic"
    ]
    
    # Locations
    locations = [
        "San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX",
        "Boston, MA", "Chicago, IL", "Denver, CO", "Los Angeles, CA",
        "San Diego, CA", "Portland, OR", "Atlanta, GA", "Miami, FL",
        "Dallas, TX", "Houston, TX", "Phoenix, AZ", "Philadelphia, PA",
        "Pittsburgh, PA", "Detroit, MI", "Minneapolis, MN", "Salt Lake City, UT",
        "Remote", "Hybrid", "Washington, DC", "Baltimore, MD", "Nashville, TN"
    ]
    
    # Skills
    all_skills = [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
        "React", "Angular", "Vue.js", "Node.js", "Express", "Django", "Flask",
        "Spring Boot", "ASP.NET", "Laravel", "Ruby on Rails", "PHP",
        "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
        "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Terraform",
        "Jenkins", "GitLab CI", "GitHub Actions", "Ansible", "Chef", "Puppet",
        "Linux", "Windows", "macOS", "Git", "SVN", "Mercurial",
        "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-learn",
        "Pandas", "NumPy", "Matplotlib", "Seaborn", "Plotly", "D3.js",
        "Tableau", "Power BI", "Looker", "Grafana", "Kibana", "Splunk",
        "REST API", "GraphQL", "gRPC", "WebSocket", "Microservices", "SOA",
        "Agile", "Scrum", "Kanban", "DevOps", "CI/CD", "TDD", "BDD",
        "Cybersecurity", "Penetration Testing", "Vulnerability Assessment",
        "Network Security", "Application Security", "Cloud Security", "DevSecOps"
    ]
    
    # Experience levels
    experience_levels = ["Entry Level", "Mid Level", "Senior Level", "Lead", "Principal"]
    
    # Generate mock data
    mock_data = []
    
    for i in range(num_jobs):
        job_title = random.choice(job_titles)
        company = random.choice(companies)
        location = random.choice(locations)
        experience_level = random.choice(experience_levels)
        
        # Generate salary range based on experience level
        base_salary = {
            "Entry Level": (60000, 90000),
            "Mid Level": (80000, 120000),
            "Senior Level": (110000, 160000),
            "Lead": (140000, 200000),
            "Principal": (180000, 250000)
        }
        
        min_salary, max_salary = base_salary[experience_level]
        salary_min = random.randint(min_salary, max_salary - 10000)
        salary_max = random.randint(salary_min + 10000, max_salary)
        
        # Generate skills (3-8 skills per job)
        num_skills = random.randint(3, 8)
        skills = random.sample(all_skills, num_skills)
        
        # Generate redirect link and apply URL
        redirect_link = f"https://example.com/job/{i+1}"
        apply_url = f"https://example.com/apply/{i+1}"
        
        mock_data.append({
            "Job_title": job_title,
            "Company": company,
            "Salary_min": salary_min,
            "Salary_max": salary_max,
            "Skills_list": str(skills),
            "Location": location,
            "Redirect_link": redirect_link,
            "Apply_url": apply_url,
            "Experience_level": experience_level
        })
    
    return pd.DataFrame(mock_data)

def save_mock_data_to_csv(filename="data/mock_job_data.csv", num_jobs=100):
    """Generate and save mock data to CSV"""
    import os
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Generate mock data
    mock_df = generate_mock_job_data(num_jobs)
    
    # Save to CSV
    mock_df.to_csv(filename, index=False)
    print(f"Mock job data saved to {filename}")
    print(f"Generated {len(mock_df)} job listings")
    
    return mock_df

def main():
    """Test the mock data generator"""
    print("Mock Job Data Generator")
    print("=" * 30)
    
    # Generate and save mock data
    df = save_mock_data_to_csv()
    
    # Show sample data
    print("\nSample Data:")
    print(df.head().to_string())
    
    # Show statistics
    print(f"\nStatistics:")
    print(f"Total jobs: {len(df)}")
    print(f"Unique companies: {df['Company'].nunique()}")
    print(f"Unique job titles: {df['Job_title'].nunique()}")
    print(f"Unique locations: {df['Location'].nunique()}")
    
    # Show salary statistics
    print(f"\nSalary Statistics:")
    print(f"Average min salary: ${df['Salary_min'].mean():,.0f}")
    print(f"Average max salary: ${df['Salary_max'].mean():,.0f}")
    
    # Show top companies
    print(f"\nTop Companies:")
    top_companies = df['Company'].value_counts().head(5)
    for company, count in top_companies.items():
        print(f"  {company}: {count} jobs")

if __name__ == "__main__":
    main()
