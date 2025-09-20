#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Job Market & Skills Analyzer
============================

一个完整的Python应用程序，帮助学生和求职者了解当前就业市场中最有价值的技术技能、工具和课程。
通过整合实时职位发布、劳工统计和薪资数据，解决职业规划信息碎片化、过时或道听途说的问题。

作者: Orange Team
版本: 1.0
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
import re
import json
from urllib.parse import urljoin, urlparse
import warnings
from typing import Dict, List, Optional, Tuple
import logging

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    logger.warning("Plotly未安装，交互式图表功能将不可用")

warnings.filterwarnings('ignore')


class JobMarketAnalyzer:
    """Job Market & Skills Analyzer 主类"""
    
    def __init__(self):
        """初始化分析器"""
        self.base_url = "https://www.onetonline.org"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 数据存储
        self.occupation_data = []
        self.skills_data = []
        self.salary_data = []
        
        # 技能关键词
        self.tech_skills = [
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'SQL', 'R', 'MATLAB',
            'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Django',
            'Flask', 'Spring', 'TensorFlow', 'PyTorch', 'Scikit-learn',
            'Pandas', 'NumPy', 'Apache Spark', 'Hadoop', 'Kubernetes',
            'Docker', 'AWS', 'Azure', 'Google Cloud', 'Git', 'Linux',
            'Machine Learning', 'Deep Learning', 'Data Science', 'Big Data',
            'Cloud Computing', 'DevOps', 'Agile', 'Scrum', 'Tableau',
            'Power BI', 'Excel', 'MongoDB', 'PostgreSQL', 'MySQL'
        ]
        
    def get_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """
        获取网页内容
        
        Args:
            url: 目标URL
            retries: 重试次数
            
        Returns:
            BeautifulSoup对象或None
        """
        for attempt in range(retries):
            try:
                logger.info(f"正在获取页面: {url} (尝试 {attempt + 1}/{retries})")
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                # 检查是否被重定向到错误页面
                if "error" in response.url.lower() or response.status_code != 200:
                    logger.warning(f"页面可能有问题: {response.url}")
                    continue
                    
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    logger.error(f"无法获取页面 {url}: {e}")
                    
        return None
    
    def get_occupation_links(self, start_url: str) -> Dict[str, str]:
        """
        从O*NET获取职业链接
        
        Args:
            start_url: 起始URL
            
        Returns:
            职业标题到URL的映射
        """
        logger.info("开始获取职业链接...")
        links = {}
        
        # 尝试多个可能的起始页面
        possible_urls = [
            start_url,
            f"{self.base_url}/find/family?f=15&g=Go",  # 计算机和数学职业
            f"{self.base_url}/find/family?f=13&g=Go",  # 商业和金融职业
            f"{self.base_url}/find/family?f=11&g=Go",  # 管理职业
        ]
        
        for url in possible_urls:
            soup = self.get_page(url)
            if not soup:
                continue
                
            # 尝试多种选择器来找到职业链接
            selectors = [
                'td.report2 > a[href*="/link/summary/"]',
                'a[href*="/link/summary/"]',
                'td > a[href*="/summary/"]',
                'a[href*="/summary/"]',
                '.report2 a',
                'table a[href*="summary"]'
            ]
            
            for selector in selectors:
                found_links = soup.select(selector)
                if found_links:
                    logger.info(f"使用选择器 '{selector}' 找到 {len(found_links)} 个链接")
                    
                    for link in found_links:
                        title = link.get_text(strip=True)
                        href = link.get('href', '')
                        
                        if title and href and 'summary' in href:
                            full_url = urljoin(self.base_url, href)
                            links[title] = full_url
                    
                    if links:
                        break
            
            if links:
                break
                
            time.sleep(1)
        
        logger.info(f"总共找到 {len(links)} 个职业链接")
        return links
    
    def scrape_occupation_details(self, title: str, url: str) -> Optional[Dict]:
        """
        爬取单个职业的详细信息
        
        Args:
            title: 职业标题
            url: 职业详情页URL
            
        Returns:
            职业数据字典
        """
        logger.info(f"正在爬取职业: {title}")
        
        soup = self.get_page(url)
        if not soup:
            return None
            
        try:
            data = {
                'title': title,
                'url': url,
                'description': '',
                'skills': [],
                'technology_skills': [],
                'education_level': '',
                'salary_median': '',
                'job_growth': '',
                'work_activities': [],
                'work_context': []
            }
            
            # 获取职业描述
            desc_selectors = [
                '.summary-description',
                '.description',
                '#description',
                '.job-description'
            ]
            
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    data['description'] = desc_elem.get_text(strip=True)
                    break
            
            # 获取技能信息
            skills_section = soup.find('section', {'id': 'skills'}) or soup.find('div', class_='skills')
            if skills_section:
                skill_links = skills_section.find_all('a')
                for link in skill_links:
                    skill_text = link.get_text(strip=True)
                    if skill_text:
                        data['skills'].append(skill_text)
                        
                        # 检查是否是技术技能
                        for tech_skill in self.tech_skills:
                            if tech_skill.lower() in skill_text.lower():
                                data['technology_skills'].append(tech_skill)
            
            # 获取薪资信息
            salary_section = soup.find('section', {'id': 'wages'}) or soup.find('div', class_='wages')
            if salary_section:
                salary_text = salary_section.get_text()
                # 提取薪资数字
                salary_match = re.search(r'\$[\d,]+', salary_text)
                if salary_match:
                    data['salary_median'] = salary_match.group()
            
            # 获取教育要求
            education_section = soup.find('section', {'id': 'education'}) or soup.find('div', class_='education')
            if education_section:
                data['education_level'] = education_section.get_text(strip=True)[:200]
            
            # 获取工作活动
            activities_section = soup.find('section', {'id': 'work-activities'}) or soup.find('div', class_='work-activities')
            if activities_section:
                activity_items = activities_section.find_all('li') or activities_section.find_all('p')
                for item in activity_items[:5]:  # 限制数量
                    activity_text = item.get_text(strip=True)
                    if activity_text:
                        data['work_activities'].append(activity_text)
            
            logger.info(f"成功爬取职业: {title}")
            return data
            
        except Exception as e:
            logger.error(f"爬取职业 {title} 时出错: {e}")
            return None
    
    def scrape_onet_data(self, max_occupations: int = 50) -> List[Dict]:
        """
        爬取O*NET数据
        
        Args:
            max_occupations: 最大职业数量
            
        Returns:
            职业数据列表
        """
        logger.info("开始爬取O*NET数据...")
        
        # 获取职业链接
        start_url = f"{self.base_url}/find/family?f=15&g=Go"
        occupation_links = self.get_occupation_links(start_url)
        
        if not occupation_links:
            logger.error("无法获取职业链接")
            return []
        
        # 限制爬取数量
        limited_links = dict(list(occupation_links.items())[:max_occupations])
        
        all_data = []
        for i, (title, url) in enumerate(limited_links.items(), 1):
            logger.info(f"进度: {i}/{len(limited_links)} - {title}")
            
            data = self.scrape_occupation_details(title, url)
            if data:
                all_data.append(data)
            
            # 添加延迟避免被封
            time.sleep(1)
            
            # 每10个职业保存一次数据
            if i % 10 == 0:
                logger.info(f"已爬取 {i} 个职业，当前数据量: {len(all_data)}")
        
        self.occupation_data = all_data
        logger.info(f"O*NET数据爬取完成，共获取 {len(all_data)} 个职业数据")
        return all_data
    
    def analyze_skills(self) -> pd.DataFrame:
        """
        分析技能数据
        
        Returns:
            技能分析结果DataFrame
        """
        if not self.occupation_data:
            logger.error("没有职业数据可供分析")
            return pd.DataFrame()
        
        logger.info("开始分析技能数据...")
        
        # 创建DataFrame
        df = pd.DataFrame(self.occupation_data)
        
        # 展开技术技能
        skills_df = df.explode('technology_skills').dropna(subset=['technology_skills'])
        
        if skills_df.empty:
            logger.warning("没有找到技术技能数据")
            return pd.DataFrame()
        
        # 技能频率统计
        skill_counts = skills_df['technology_skills'].value_counts()
        
        # 按职业统计技能
        skills_by_occupation = skills_df.groupby('title')['technology_skills'].apply(list).to_dict()
        
        # 创建分析结果
        analysis_results = []
        for skill, count in skill_counts.items():
            analysis_results.append({
                'skill': skill,
                'frequency': count,
                'percentage': (count / len(df)) * 100,
                'occupations': [title for title, skills in skills_by_occupation.items() if skill in skills]
            })
        
        skills_analysis_df = pd.DataFrame(analysis_results)
        skills_analysis_df = skills_analysis_df.sort_values('frequency', ascending=False)
        
        logger.info(f"技能分析完成，共分析 {len(skills_analysis_df)} 个技能")
        return skills_analysis_df
    
    def create_visualizations(self, skills_df: pd.DataFrame):
        """
        创建可视化图表
        
        Args:
            skills_df: 技能分析DataFrame
        """
        if skills_df.empty:
            logger.error("没有数据可供可视化")
            return
        
        logger.info("开始创建可视化图表...")
        
        # 设置图表样式
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # 1. 技能频率条形图
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Job Market Skills Analysis - O*NET Data', fontsize=16, fontweight='bold')
        
        # 前20个技能
        top_skills = skills_df.head(20)
        
        # 技能频率图
        axes[0, 0].barh(range(len(top_skills)), top_skills['frequency'], color='skyblue')
        axes[0, 0].set_yticks(range(len(top_skills)))
        axes[0, 0].set_yticklabels(top_skills['skill'])
        axes[0, 0].set_xlabel('Frequency')
        axes[0, 0].set_title('Top 20 Most In-Demand Skills')
        axes[0, 0].invert_yaxis()
        
        # 技能百分比饼图
        top_10_skills = skills_df.head(10)
        axes[0, 1].pie(top_10_skills['frequency'], labels=top_10_skills['skill'], autopct='%1.1f%%')
        axes[0, 1].set_title('Top 10 Skills Distribution')
        
        # 技能频率趋势
        axes[1, 0].plot(range(len(top_skills)), top_skills['frequency'], marker='o', linewidth=2)
        axes[1, 0].set_xlabel('Skill Rank')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Skill Frequency Trend')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 技能百分比柱状图
        top_10_skills = skills_df.head(10)
        axes[1, 1].bar(range(len(top_10_skills)), top_10_skills['percentage'], color='lightcoral')
        axes[1, 1].set_xticks(range(len(top_10_skills)))
        axes[1, 1].set_xticklabels(top_10_skills['skill'], rotation=45, ha='right')
        axes[1, 1].set_ylabel('Percentage (%)')
        axes[1, 1].set_title('Top 10 Skills Percentage')
        
        plt.tight_layout()
        plt.show()
        
        # 2. 创建交互式图表
        self.create_interactive_charts(skills_df)
        
        logger.info("可视化图表创建完成")
    
    def create_interactive_charts(self, skills_df: pd.DataFrame):
        """
        创建交互式图表
        
        Args:
            skills_df: 技能分析DataFrame
        """
        if not PLOTLY_AVAILABLE:
            logger.warning("Plotly未安装，跳过交互式图表创建")
            return
            
        # 创建子图
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Top Skills Frequency', 'Skills Distribution', 
                          'Skills by Category', 'Skills Trend'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )
        
        top_15_skills = skills_df.head(15)
        
        # 技能频率条形图
        fig.add_trace(
            go.Bar(x=top_15_skills['skill'], y=top_15_skills['frequency'],
                   name='Frequency', marker_color='lightblue'),
            row=1, col=1
        )
        
        # 技能分布饼图
        top_8_skills = skills_df.head(8)
        fig.add_trace(
            go.Pie(labels=top_8_skills['skill'], values=top_8_skills['frequency'],
                   name="Distribution"),
            row=1, col=2
        )
        
        # 技能散点图
        fig.add_trace(
            go.Scatter(x=top_15_skills['skill'], y=top_15_skills['percentage'],
                       mode='markers+lines', name='Percentage',
                       marker=dict(size=10, color='red')),
            row=2, col=1
        )
        
        # 技能百分比柱状图
        fig.add_trace(
            go.Bar(x=top_10_skills['skill'], y=top_10_skills['percentage'],
                   name='Percentage', marker_color='lightgreen'),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="Interactive Job Market Skills Analysis",
            showlegend=False,
            height=800
        )
        
        fig.show()
    
    def search_skills(self, query: str) -> pd.DataFrame:
        """
        搜索特定技能
        
        Args:
            query: 搜索查询
            
        Returns:
            匹配的技能数据
        """
        if not self.occupation_data:
            logger.error("没有数据可供搜索")
            return pd.DataFrame()
        
        df = pd.DataFrame(self.occupation_data)
        
        # 搜索包含查询的职业
        mask = df['title'].str.contains(query, case=False, na=False) | \
               df['description'].str.contains(query, case=False, na=False)
        
        results = df[mask]
        
        if not results.empty:
            logger.info(f"找到 {len(results)} 个匹配的职业")
        else:
            logger.info("没有找到匹配的职业")
        
        return results
    
    def get_skill_recommendations(self, target_role: str) -> Dict:
        """
        获取技能推荐
        
        Args:
            target_role: 目标角色
            
        Returns:
            技能推荐字典
        """
        if not self.occupation_data:
            return {}
        
        # 搜索相关职业
        related_occupations = self.search_skills(target_role)
        
        if related_occupations.empty:
            return {"error": "没有找到相关职业"}
        
        # 收集所有技能
        all_skills = []
        for skills in related_occupations['technology_skills']:
            if isinstance(skills, list):
                all_skills.extend(skills)
        
        # 统计技能频率
        skill_counts = pd.Series(all_skills).value_counts()
        
        recommendations = {
            "target_role": target_role,
            "related_occupations": len(related_occupations),
            "top_skills": skill_counts.head(10).to_dict(),
            "skill_categories": {
                "programming": [skill for skill in skill_counts.index if skill in ['Python', 'Java', 'JavaScript', 'C++', 'C#', 'R']],
                "data_analysis": [skill for skill in skill_counts.index if skill in ['SQL', 'Pandas', 'NumPy', 'Tableau', 'Power BI']],
                "cloud": [skill for skill in skill_counts.index if skill in ['AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes']],
                "machine_learning": [skill for skill in skill_counts.index if skill in ['Machine Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn']]
            }
        }
        
        return recommendations
    
    def save_data(self, filename: str = "job_market_data.json"):
        """
        保存数据到文件
        
        Args:
            filename: 文件名
        """
        data_to_save = {
            "occupation_data": self.occupation_data,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_occupations": len(self.occupation_data)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已保存到 {filename}")
    
    def load_data(self, filename: str = "job_market_data.json"):
        """
        从文件加载数据
        
        Args:
            filename: 文件名
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.occupation_data = data.get("occupation_data", [])
            logger.info(f"从 {filename} 加载了 {len(self.occupation_data)} 个职业数据")
            
        except FileNotFoundError:
            logger.error(f"文件 {filename} 不存在")
        except Exception as e:
            logger.error(f"加载数据时出错: {e}")


def main():
    """主函数"""
    print("=" * 60)
    print("Job Market & Skills Analyzer")
    print("Orange Team - 职业市场技能分析器")
    print("=" * 60)
    
    # 创建分析器实例
    analyzer = JobMarketAnalyzer()
    
    while True:
        print("\n请选择操作:")
        print("1. 爬取O*NET数据")
        print("2. 分析技能数据")
        print("3. 搜索特定技能/职业")
        print("4. 获取技能推荐")
        print("5. 创建可视化图表")
        print("6. 保存数据")
        print("7. 加载数据")
        print("8. 退出")
        
        choice = input("\n请输入选择 (1-8): ").strip()
        
        if choice == '1':
            max_occupations = input("请输入要爬取的最大职业数量 (默认50): ").strip()
            max_occupations = int(max_occupations) if max_occupations.isdigit() else 50
            
            print(f"\n开始爬取最多 {max_occupations} 个职业...")
            data = analyzer.scrape_onet_data(max_occupations)
            print(f"爬取完成，共获取 {len(data)} 个职业数据")
            
        elif choice == '2':
            if not analyzer.occupation_data:
                print("请先爬取数据!")
                continue
                
            skills_df = analyzer.analyze_skills()
            if not skills_df.empty:
                print("\n技能分析结果:")
                print(skills_df.head(10).to_string())
            else:
                print("没有找到技能数据")
                
        elif choice == '3':
            if not analyzer.occupation_data:
                print("请先爬取数据!")
                continue
                
            query = input("请输入搜索关键词: ").strip()
            if query:
                results = analyzer.search_skills(query)
                if not results.empty:
                    print(f"\n找到 {len(results)} 个匹配结果:")
                    print(results[['title', 'description']].head().to_string())
                else:
                    print("没有找到匹配结果")
                    
        elif choice == '4':
            if not analyzer.occupation_data:
                print("请先爬取数据!")
                continue
                
            target_role = input("请输入目标角色 (如: data scientist): ").strip()
            if target_role:
                recommendations = analyzer.get_skill_recommendations(target_role)
                if "error" not in recommendations:
                    print(f"\n{target_role} 技能推荐:")
                    print(f"相关职业数量: {recommendations['related_occupations']}")
                    print("\n热门技能:")
                    for skill, count in recommendations['top_skills'].items():
                        print(f"  {skill}: {count} 次")
                else:
                    print(recommendations["error"])
                    
        elif choice == '5':
            if not analyzer.occupation_data:
                print("请先爬取数据!")
                continue
                
            skills_df = analyzer.analyze_skills()
            if not skills_df.empty:
                analyzer.create_visualizations(skills_df)
            else:
                print("没有数据可供可视化")
                
        elif choice == '6':
            if not analyzer.occupation_data:
                print("没有数据可保存!")
                continue
                
            filename = input("请输入文件名 (默认: job_market_data.json): ").strip()
            filename = filename if filename else "job_market_data.json"
            analyzer.save_data(filename)
            
        elif choice == '7':
            filename = input("请输入文件名 (默认: job_market_data.json): ").strip()
            filename = filename if filename else "job_market_data.json"
            analyzer.load_data(filename)
            
        elif choice == '8':
            print("感谢使用 Job Market & Skills Analyzer!")
            break
            
        else:
            print("无效选择，请重新输入!")


if __name__ == "__main__":
    main()
