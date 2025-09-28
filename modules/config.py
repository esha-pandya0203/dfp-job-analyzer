#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Job Market & Skills Analyzer - Configuration File
===============================================

Contains all configuration options and constant definitions

Author: Orange Team
Version: 1.0
"""

import os
from typing import Dict, List, Optional

# Basic Configuration
class Config:
    """Main configuration class"""
    
    # Project Information
    PROJECT_NAME = "Job Market & Skills Analyzer"
    VERSION = "1.0"
    AUTHOR = "Orange Team"
    
    # Data Source Configuration
    ONET_BASE_URL = "https://www.onetonline.org"
    BLS_API_BASE_URL = "https://api.bls.gov/publicAPI/v2"
    
    # Scraper Configuration
    REQUEST_DELAY = 1  # Request interval (seconds)
    MAX_RETRIES = 3    # Maximum retry attempts
    TIMEOUT = 10       # Request timeout (seconds)
    MAX_OCCUPATIONS = 100  # Default maximum number of occupations
    
    # Request Headers Configuration
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # Technical Skills Keywords
    TECH_SKILLS = [
        # Programming Languages
        'Python', 'Java', 'JavaScript', 'C++', 'C#', 'R', 'MATLAB', 'Go', 'Rust', 'Swift',
        'Kotlin', 'Scala', 'PHP', 'Ruby', 'Perl', 'TypeScript', 'Dart',
        
        # Web Development
        'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask',
        'Spring', 'Express.js', 'Laravel', 'ASP.NET', 'jQuery', 'Bootstrap',
        
        # Data Science and Machine Learning
        'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'SciPy',
        'Apache Spark', 'Hadoop', 'Keras', 'OpenCV', 'NLTK', 'spaCy',
        
        # Databases
        'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
        'Oracle', 'SQLite', 'Cassandra', 'Neo4j',
        
        # Cloud Computing and DevOps
        'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Terraform',
        'Jenkins', 'GitLab CI', 'GitHub Actions', 'Ansible', 'Chef', 'Puppet',
        
        # Tools and Platforms
        'Git', 'Linux', 'Windows', 'macOS', 'Tableau', 'Power BI', 'Excel',
        'Jupyter', 'Apache Kafka', 'RabbitMQ', 'Apache Airflow',
        
        # Concepts and Frameworks
        'Machine Learning', 'Deep Learning', 'Data Science', 'Big Data',
        'Cloud Computing', 'DevOps', 'Agile', 'Scrum', 'Microservices',
        'REST API', 'GraphQL', 'Blockchain', 'IoT', 'Cybersecurity'
    ]
    
    # Occupation Categories
    OCCUPATION_CATEGORIES = {
        'data_science': ['data scientist', 'data analyst', 'data engineer', 'machine learning engineer'],
        'software_development': ['software developer', 'software engineer', 'full stack developer', 'backend developer'],
        'business': ['business analyst', 'product manager', 'project manager', 'business intelligence analyst'],
        'cloud_devops': ['cloud architect', 'devops engineer', 'site reliability engineer', 'cloud engineer'],
        'cybersecurity': ['cybersecurity analyst', 'security engineer', 'penetration tester', 'security architect']
    }
    
    # File Path Configuration
    DATA_DIR = "data"
    OUTPUT_DIR = "output"
    LOG_DIR = "logs"
    
    # Default File Names
    DEFAULT_DATA_FILE = "job_market_data.json"
    DEFAULT_SKILLS_FILE = "skills_analysis.csv"
    DEFAULT_REPORT_FILE = "analysis_report.html"
    
    # Visualization Configuration
    CHART_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                   '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    CHART_STYLE = 'seaborn-v0_8-whitegrid'
    FIGURE_SIZE = (12, 8)
    
    # BLS API Configuration
    BLS_RATE_LIMIT = 0.5  # Requests per second
    BLS_DEFAULT_YEARS = [2020, 2021, 2022, 2023]
    
    # Logging Configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        directories = [cls.DATA_DIR, cls.OUTPUT_DIR, cls.LOG_DIR]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_skill_category(cls, skill: str) -> Optional[str]:
        """
        Get skill category
        
        Args:
            skill: Skill name
            
        Returns:
            Skill category or None
        """
        skill_lower = skill.lower()
        
        if any(keyword in skill_lower for keyword in ['python', 'java', 'javascript', 'c++', 'c#', 'r']):
            return 'programming'
        elif any(keyword in skill_lower for keyword in ['sql', 'pandas', 'numpy', 'tableau', 'power bi']):
            return 'data_analysis'
        elif any(keyword in skill_lower for keyword in ['aws', 'azure', 'google cloud', 'docker', 'kubernetes']):
            return 'cloud'
        elif any(keyword in skill_lower for keyword in ['machine learning', 'tensorflow', 'pytorch', 'scikit-learn']):
            return 'machine_learning'
        elif any(keyword in skill_lower for keyword in ['html', 'css', 'react', 'angular', 'vue']):
            return 'web_development'
        else:
            return 'other'


# Environment-specific Configuration
class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    MAX_OCCUPATIONS = 20  # Use less data during development


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    LOG_LEVEL = "INFO"
    MAX_OCCUPATIONS = 200  # Production environment can use more data


class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    LOG_LEVEL = "WARNING"
    MAX_OCCUPATIONS = 5  # Use minimal data for testing


# Configuration Factory
def get_config(env: str = None) -> Config:
    """
    Get configuration object
    
    Args:
        env: Environment name ('development', 'production', 'testing')
        
    Returns:
        Configuration object
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return config_map.get(env, DevelopmentConfig)


# Default configuration instance
config = get_config()
