BLS_SOC_MAPPING = {
    # Computer Programmers
    "15-1251": {
        "soc_title": "Computer Programmers",
        "job_titles": ['Computer Programmers', 'AI/ML', 'AI', 'ML', 'Artificial Intelligence', 'Machine Learning', 
                       'Generative AI', 'Gen AI', 'LLM', 'Software Engineer with Poly Mid', 
                       'Cloud', 'Cloud Engineer', 'IT Security', 'IT', 'Support Technician', 'IT Support', 
                       'Product Support Engineer', 'Lead', 'Technical Support', 'Windows Engineer', 
                       'Tech Leader', 'CIO', 'Technology Officer', 'Azure', 'AWS', 'Technology', 
                       'Reliability Engineer', 'Customer Success Manager', 'Monitoring Center Analyst', 
                       'Customer Success', 'SDSA', 'Site Reliability Engineer', 'CCaaS', 'IAM', 
                       'GEN AI Architect', 'Technoogy & Innovation', 'Platform Engineer'],
        "category": "Programming & Development"
    },
    
    # Software Developers
    "15-1252": {
        "soc_title": "Software Developers",
        "job_titles": ['DevOps', 'Software Developer', 'Release Manager', 'PaaS Lead', 
                       'Platorm Infrastructure Engineer', 'RHEL Engineer', 'RHEL', 
                       'Experienced Software Engineer', 'Software', 'Developer', 
                       'Frontend engineer', 'Backend Engineer', 'Full Stack', 
                       'Frontend', 'Backend', 'React'],
        "category": "Software Development"
    },
    
    # Software Quality Assurance Analysts and Testers
    "15-1253": {
        "soc_title": "Software Quality Assurance Analysts and Testers",
        "job_titles": ['Operations', 'General Manager', 'Project Coordinator', 
                       'Administrative Business Partner', 'Logistics', 'Customer Experience Specialist', 
                       'Brand Manager', 'Plant Manager', 'Demand Planner', 
                       'Workforce Management', 'Operational', 'Supply Chain', 'Coordinator', 
                       'Extruder Area Manager', 'Administrative Assistant', 'Operating', 
                       'Commodities', 'People, Culture, & Performance', 'Executive Assistant', 
                       'Regional Manager', 'Assistant', 'Concierge', 'Learning & Development', 
                       'Marketing', 'Executive', 'VP', 'Vice President', 
                       'Field Deployment Lead', 'Warehouse Lead', 'Regional Sales', 
                       'Store Manager', 'HR', 'Retail', 'Recruiter', 'QA', 'Quality Assurance', 
                       'Tester', 'Quality Control'],
        "category": "Quality Assurance & Testing"
    },
    
    # Data Scientists
    "15-2050": {
        "soc_title": "Data Scientists",
        "job_titles": [ 'Data Analyst', 'Data Scientist', 'Data Engineer',
            'Data', 'Business Intelligence Analyst', 
            'Analytics', 'Analyst', 'PowerBI Developer', 
            'Quantitative', 'Applied Scientist', 'Research Scientist', 
            'Decision Science', 'Scientist' 
        ],
        "category": "Data & Analytics"
    },
    
    # Computer and Information Systems Managers
    "11-3021": {
        "soc_title": "Computer and Information Systems Managers",
        "job_titles": ['Computer and Information Systems Managers', 'Technical Product Manager', 'Product', 
                       'Wealth Management Analyst', ' Creative Strategist', 
                       'UX', 'UI', 'Solutions'],
        "category": "Management & Leadership"
    },
    
    # Computer Network Architects
    "15-1241": {
        "soc_title": "Computer Network Architects",
        "job_titles": ['Network Engineer', 
            'Information Security', 'SOC', 'Cybersecurity', 
            'Cyber', 'Security', 'Compliance', 'Information System', 
            'Help Desk Support', 'Engineer, Data Center', 'Security Risk Analyst', 
            'Privacy', 'Incident Response', 'Data Center', 'Strategy',
              'Vulnerability', 'Network', 'Threat Analyst', 'Technology and Innovation', 
              'Security Operations', 'Counterintelligence', 'Risk', 'Internal Audit',
                'Incident', 'Threat', 'Anti-Money Laundering',
                  'Comply-to-Connect & Endpoint Policy Analyst'],
        "category": "Cybersecurity & Networks"
    },
    
}

# Reverse mapping: Job Title to SOC Code
def create_reverse_mapping():
    """Create reverse mapping from job titles to SOC codes"""
    reverse_mapping = {}
    
    for soc_code, data in BLS_SOC_MAPPING.items():
        normalized_title = data['soc_title'].lower().strip() 
        reverse_mapping[normalized_title] = {
            'soc_code': soc_code, 
            'category': data['category']
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

'''
Returns the matching SOC code from BLS to the given job title. 
'''
def match_job_title_to_soc_code(job_title):
    for soc_code, values in BLS_SOC_MAPPING.items():
        if job_title in values['job_titles']:
            return soc_code 

'''
Returns all SOC codes from BLS that match the given job title. 
'''
def find_all_matching_soc_codes(job_title):
    matched_codes = set() 
    text = job_title.split(' ') 

    for soc_code, values in BLS_SOC_MAPPING.items():
        for title in values['job_titles']:
            for word in text: 
                if word.upper() == title.upper(): 
                    matched_codes.add(soc_code)
    
    return matched_codes

if __name__ == "__main__":
    validate_mapping()