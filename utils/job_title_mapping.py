#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Job Title to BLS SOC Code Mapping
=================================

This module provides comprehensive mapping between job titles and BLS SOC codes
for the tech industry, based on the project requirements.

Author: Project Team
Version: 1.0
"""

# BLS SOC Code to Job Titles Mapping
# Based on: https://www.bls.gov/oes/2023/may/oes_stru.htm#15-0000

BLS_SOC_MAPPING = {
    # Computer Programmers
    "15-1251": {
        "soc_title": "Computer Programmers",
        "job_titles": [
            "Computer Programmer",
            "Programmer",
            "Software Programmer",
            "Application Programmer",
            "Systems Programmer",
            "Web Programmer",
            "Mobile App Developer",
            "Game Developer",
            "AI/ML Engineer",
            "Machine Learning Engineer",
            "Artificial Intelligence Engineer",
            "Cloud Engineer",
            "Cloud Developer",
            "Cloud Solutions Engineer",
            "AWS Engineer",
            "Azure Engineer",
            "Google Cloud Engineer"
        ],
        "category": "Programming & Development"
    },
    
    # Software Developers
    "15-1252": {
        "soc_title": "Software Developers",
        "job_titles": [
            "Software Developer",
            "Software Engineer",
            "Full Stack Developer",
            "Frontend Developer",
            "Backend Developer",
            "Web Developer",
            "Mobile Developer",
            "iOS Developer",
            "Android Developer",
            "React Developer",
            "Angular Developer",
            "Vue.js Developer",
            "Node.js Developer",
            "Python Developer",
            "Java Developer",
            "C# Developer",
            "DevOps Engineer",
            "DevOps Developer",
            "Site Reliability Engineer",
            "Platform Engineer",
            "Infrastructure Engineer"
        ],
        "category": "Software Development"
    },
    
    # Software Quality Assurance Analysts and Testers
    "15-1253": {
        "soc_title": "Software Quality Assurance Analysts and Testers",
        "job_titles": [
            "QA Engineer",
            "Quality Assurance Engineer",
            "Software Tester",
            "Test Engineer",
            "Automation Engineer",
            "QA Analyst",
            "Test Analyst",
            "Performance Engineer",
            "Security Tester",
            "Manual Tester",
            "Automated Tester",
            "Operations Engineer",
            "Operations Analyst"
        ],
        "category": "Quality Assurance & Testing"
    },
    
    # Data Scientists
    "15-2050": {
        "soc_title": "Data Scientists",
        "job_titles": [
            "Data Analyst",
            "Data Scientist",
            "Data Engineer",
            "Business Analyst",
            "Analytics Engineer",
            "Data Architect",
            "ML Engineer",
            "Data Pipeline Engineer",
            "ETL Developer",
            "Big Data Engineer",
            "Data Warehouse Engineer",
            "Business Intelligence Analyst",
            "BI Analyst",
            "Research Scientist",
            "Quantitative Analyst",
            "Statistician"
        ],
        "category": "Data & Analytics"
    },
    
    # Computer and Information Systems Managers
    "11-3021": {
        "soc_title": "Computer and Information Systems Managers",
        "job_titles": [
            "Technical Product Manager",
            "Product Manager",
            "Engineering Manager",
            "Software Engineering Manager",
            "Development Manager",
            "IT Manager",
            "Technology Manager",
            "Technical Lead",
            "Team Lead",
            "Scrum Master",
            "Project Manager",
            "Program Manager",
            "Solutions Architect",
            "Technical Architect",
            "Enterprise Architect"
        ],
        "category": "Management & Leadership"
    },
    
    # Computer Network Architects
    "15-1241": {
        "soc_title": "Computer Network Architects",
        "job_titles": [
            "Cybersecurity Engineer",
            "Cybersecurity Analyst",
            "Security Engineer",
            "Information Security Engineer",
            "Network Security Engineer",
            "Security Architect",
            "Penetration Tester",
            "Ethical Hacker",
            "Security Consultant",
            "Network Engineer",
            "Systems Administrator",
            "IT Security Specialist",
            "Cloud Security Engineer",
            "DevSecOps Engineer"
        ],
        "category": "Cybersecurity & Networks"
    },
    
    # Additional IT Support and Operations
    "15-1230": {
        "soc_title": "Computer Support Specialists",
        "job_titles": [
            "IT Support Specialist",
            "Help Desk Technician",
            "Technical Support",
            "Desktop Support",
            "IT Technician",
            "System Administrator",
            "IT Administrator",
            "Network Administrator",
            "Database Administrator",
            "DBA"
        ],
        "category": "IT Support & Operations"
    }
}

# Reverse mapping: Job Title to SOC Code
def create_reverse_mapping():
    """Create reverse mapping from job titles to SOC codes"""
    reverse_mapping = {}
    
    for soc_code, data in BLS_SOC_MAPPING.items():
        for job_title in data["job_titles"]:
            # Normalize job title for matching
            normalized_title = job_title.lower().strip()
            reverse_mapping[normalized_title] = {
                "soc_code": soc_code,
                "soc_title": data["soc_title"],
                "category": data["category"],
                "original_title": job_title
            }
    
    return reverse_mapping

# Create the reverse mapping
JOB_TITLE_TO_SOC = create_reverse_mapping()

def find_soc_code(job_title):
    """
    Find SOC code for a given job title
    
    Args:
        job_title (str): The job title to search for
        
    Returns:
        dict: SOC code information or None if not found
    """
    if not job_title:
        return None
    
    # Normalize the input
    normalized_title = job_title.lower().strip()
    
    # Direct match
    if normalized_title in JOB_TITLE_TO_SOC:
        return JOB_TITLE_TO_SOC[normalized_title]
    
    # Partial match - check if any keywords match
    title_words = normalized_title.split()
    for word in title_words:
        if len(word) > 3:  # Only check words longer than 3 characters
            for mapped_title, soc_info in JOB_TITLE_TO_SOC.items():
                if word in mapped_title or mapped_title in word:
                    return soc_info
    
    return None

def get_all_job_titles():
    """Get all job titles in the mapping"""
    all_titles = []
    for data in BLS_SOC_MAPPING.values():
        all_titles.extend(data["job_titles"])
    return sorted(all_titles)

def get_job_titles_by_category(category):
    """Get job titles by category"""
    titles = []
    for data in BLS_SOC_MAPPING.values():
        if data["category"] == category:
            titles.extend(data["job_titles"])
    return sorted(titles)

def get_categories():
    """Get all available categories"""
    categories = set()
    for data in BLS_SOC_MAPPING.values():
        categories.add(data["category"])
    return sorted(list(categories))

# Validation function
def validate_mapping():
    """Validate the mapping data"""
    print("Validating BLS SOC Mapping...")
    print("=" * 50)
    
    total_titles = 0
    for soc_code, data in BLS_SOC_MAPPING.items():
        title_count = len(data["job_titles"])
        total_titles += title_count
        print(f"{soc_code}: {data['soc_title']} - {title_count} job titles")
    
    print(f"\nTotal job titles mapped: {total_titles}")
    print(f"Total SOC codes: {len(BLS_SOC_MAPPING)}")
    print(f"Categories: {len(get_categories())}")
    
    # Test reverse mapping
    test_titles = ["Software Developer", "Data Analyst", "Cybersecurity Engineer"]
    print(f"\nTesting reverse mapping:")
    for title in test_titles:
        result = find_soc_code(title)
        if result:
            print(f"  {title} -> {result['soc_code']} ({result['soc_title']})")
        else:
            print(f"  {title} -> Not found")

if __name__ == "__main__":
    validate_mapping()
