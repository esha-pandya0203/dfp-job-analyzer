#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Job Market & Skills Analyzer - 配置文件
====================================

包含所有配置选项和常量定义

作者: Orange Team
版本: 1.0
"""

import os
from typing import Dict, List, Optional

# 基础配置
class Config:
    """主配置类"""
    
    # 项目信息
    PROJECT_NAME = "Job Market & Skills Analyzer"
    VERSION = "1.0"
    AUTHOR = "Orange Team"
    
    # 数据源配置
    ONET_BASE_URL = "https://www.onetonline.org"
    BLS_API_BASE_URL = "https://api.bls.gov/publicAPI/v2"
    
    # 爬虫配置
    REQUEST_DELAY = 1  # 请求间隔（秒）
    MAX_RETRIES = 3    # 最大重试次数
    TIMEOUT = 10       # 请求超时时间（秒）
    MAX_OCCUPATIONS = 100  # 默认最大职业数量
    
    # 请求头配置
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # 技术技能关键词
    TECH_SKILLS = [
        # 编程语言
        'Python', 'Java', 'JavaScript', 'C++', 'C#', 'R', 'MATLAB', 'Go', 'Rust', 'Swift',
        'Kotlin', 'Scala', 'PHP', 'Ruby', 'Perl', 'TypeScript', 'Dart',
        
        # Web开发
        'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask',
        'Spring', 'Express.js', 'Laravel', 'ASP.NET', 'jQuery', 'Bootstrap',
        
        # 数据科学和机器学习
        'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'SciPy',
        'Apache Spark', 'Hadoop', 'Keras', 'OpenCV', 'NLTK', 'spaCy',
        
        # 数据库
        'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
        'Oracle', 'SQLite', 'Cassandra', 'Neo4j',
        
        # 云计算和DevOps
        'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Terraform',
        'Jenkins', 'GitLab CI', 'GitHub Actions', 'Ansible', 'Chef', 'Puppet',
        
        # 工具和平台
        'Git', 'Linux', 'Windows', 'macOS', 'Tableau', 'Power BI', 'Excel',
        'Jupyter', 'Apache Kafka', 'RabbitMQ', 'Apache Airflow',
        
        # 概念和框架
        'Machine Learning', 'Deep Learning', 'Data Science', 'Big Data',
        'Cloud Computing', 'DevOps', 'Agile', 'Scrum', 'Microservices',
        'REST API', 'GraphQL', 'Blockchain', 'IoT', 'Cybersecurity'
    ]
    
    # 职业分类
    OCCUPATION_CATEGORIES = {
        'data_science': ['data scientist', 'data analyst', 'data engineer', 'machine learning engineer'],
        'software_development': ['software developer', 'software engineer', 'full stack developer', 'backend developer'],
        'business': ['business analyst', 'product manager', 'project manager', 'business intelligence analyst'],
        'cloud_devops': ['cloud architect', 'devops engineer', 'site reliability engineer', 'cloud engineer'],
        'cybersecurity': ['cybersecurity analyst', 'security engineer', 'penetration tester', 'security architect']
    }
    
    # 文件路径配置
    DATA_DIR = "data"
    OUTPUT_DIR = "output"
    LOG_DIR = "logs"
    
    # 默认文件名
    DEFAULT_DATA_FILE = "job_market_data.json"
    DEFAULT_SKILLS_FILE = "skills_analysis.csv"
    DEFAULT_REPORT_FILE = "analysis_report.html"
    
    # 可视化配置
    CHART_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                   '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    CHART_STYLE = 'seaborn-v0_8-whitegrid'
    FIGURE_SIZE = (12, 8)
    
    # BLS API配置
    BLS_RATE_LIMIT = 0.5  # 每秒请求数
    BLS_DEFAULT_YEARS = [2020, 2021, 2022, 2023]
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def create_directories(cls):
        """创建必要的目录"""
        directories = [cls.DATA_DIR, cls.OUTPUT_DIR, cls.LOG_DIR]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_skill_category(cls, skill: str) -> Optional[str]:
        """
        获取技能分类
        
        Args:
            skill: 技能名称
            
        Returns:
            技能分类或None
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


# 环境特定配置
class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    MAX_OCCUPATIONS = 20  # 开发时使用较少数据


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = "INFO"
    MAX_OCCUPATIONS = 200  # 生产环境可以使用更多数据


class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    LOG_LEVEL = "WARNING"
    MAX_OCCUPATIONS = 5  # 测试时使用最少数据


# 配置工厂
def get_config(env: str = None) -> Config:
    """
    获取配置对象
    
    Args:
        env: 环境名称 ('development', 'production', 'testing')
        
    Returns:
        配置对象
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return config_map.get(env, DevelopmentConfig)


# 默认配置实例
config = get_config()
