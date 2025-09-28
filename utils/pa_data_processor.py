#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PA州职位数据分析脚本
功能：合并多个CSV文件，提取PA州数据，清洗数据并提取技能
作者：Fan
"""

import pandas as pd
import numpy as np
import os
import re
import glob
from typing import List, Dict, Any
import warnings
warnings.filterwarnings('ignore')

class PADataProcessor:
    def __init__(self, data_folder_path: str):
        """
        初始化PA数据处理器
        
        Args:
            data_folder_path: CSV文件所在的文件夹路径
        """
        self.data_folder_path = data_folder_path
        self.pa_keywords = [
            'PA', 'Pennsylvania', 'Philadelphia', 'Pittsburgh', 
            'Harrisburg', 'Allentown', 'Erie', 'Reading', 'Scranton',
            'Bethlehem', 'Lancaster', 'Altoona', 'York', 'State College'
        ]
        
    def find_csv_files(self) -> List[str]:
        """查找所有CSV文件"""
        csv_pattern = os.path.join(self.data_folder_path, "*.csv")
        csv_files = glob.glob(csv_pattern)
        print(f"找到 {len(csv_files)} 个CSV文件:")
        for file in csv_files:
            print(f"  - {os.path.basename(file)}")
        return csv_files
    
    def load_and_combine_csvs(self) -> pd.DataFrame:
        """加载并合并所有CSV文件"""
        csv_files = self.find_csv_files()
        
        if not csv_files:
            raise ValueError("未找到CSV文件")
        
        all_dataframes = []
        
        for file_path in csv_files:
            try:
                print(f"\n正在处理: {os.path.basename(file_path)}")
                
                # 尝试不同的编码方式读取CSV
                encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
                df = None
                
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        print(f"  成功读取，编码: {encoding}, 行数: {len(df)}")
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is None:
                    print(f"  警告: 无法读取文件 {file_path}")
                    continue
                
                # 添加来源文件信息
                df['source_file'] = os.path.basename(file_path)
                all_dataframes.append(df)
                
            except Exception as e:
                print(f"  错误: 处理文件 {file_path} 时出错: {str(e)}")
                continue
        
        if not all_dataframes:
            raise ValueError("没有成功读取任何CSV文件")
        
        # 合并所有数据框
        combined_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
        print(f"\n合并完成，总行数: {len(combined_df)}")
        
        return combined_df
    
    def filter_pa_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """筛选PA州的数据"""
        print("\n开始筛选PA州数据...")
        
        # 检查Location列是否存在
        location_columns = ['Location', 'location', 'LOCATION', 'job_location', 'Job_Location']
        location_col = None
        
        for col in location_columns:
            if col in df.columns:
                location_col = col
                break
        
        if location_col is None:
            print("警告: 未找到Location列，将使用所有数据")
            return df
        
        print(f"使用Location列: {location_col}")
        
        # 创建PA州筛选条件
        pa_condition = pd.Series([False] * len(df))
        
        for keyword in self.pa_keywords:
            # 检查是否包含PA相关关键词
            keyword_condition = df[location_col].astype(str).str.contains(
                keyword, case=False, na=False
            )
            pa_condition = pa_condition | keyword_condition
        
        pa_df = df[pa_condition].copy()
        
        print(f"PA州数据筛选完成:")
        print(f"  原始数据: {len(df)} 行")
        print(f"  PA州数据: {len(pa_df)} 行")
        print(f"  筛选比例: {len(pa_df)/len(df)*100:.1f}%")
        
        return pa_df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """数据清洗"""
        print("\n开始数据清洗...")
        
        original_count = len(df)
        
        # 1. 删除完全空白的行
        df = df.dropna(how='all')
        
        # 2. 处理重复数据
        df = df.drop_duplicates()
        
        # 3. 标准化列名
        column_mapping = {
            'Job_title': 'job_title',
            'Company': 'company',
            'Salary_min': 'salary_min',
            'Salary_max': 'salary_max',
            'Skills_list': 'skills_list',
            'Location': 'location',
            'Redirect_link': 'redirect_link',
            'Experience_level': 'experience_level',
            'BLS_soc_code': 'bls_soc_code',
            'Description': 'description',
            'Job_Description': 'description'
        }
        
        df = df.rename(columns=column_mapping)
        
        # 4. 清洗薪资数据
        if 'salary_min' in df.columns:
            df['salary_min'] = self._clean_salary(df['salary_min'])
        if 'salary_max' in df.columns:
            df['salary_max'] = self._clean_salary(df['salary_max'])
        
        # 5. 清洗技能列表
        if 'skills_list' in df.columns:
            df['skills_list'] = df['skills_list'].apply(self._clean_skills_list)
        
        # 6. 清洗位置信息
        if 'location' in df.columns:
            df['location'] = df['location'].str.strip()
        
        print(f"数据清洗完成:")
        print(f"  清洗前行数: {original_count}")
        print(f"  清洗后行数: {len(df)}")
        print(f"  删除行数: {original_count - len(df)}")
        
        return df
    
    def _clean_salary(self, salary_series: pd.Series) -> pd.Series:
        """清洗薪资数据"""
        def extract_salary(salary_str):
            if pd.isna(salary_str):
                return None
            
            salary_str = str(salary_str)
            # 提取数字
            numbers = re.findall(r'\d+(?:,\d{3})*(?:\.\d{2})?', salary_str)
            if numbers:
                # 取第一个数字，去掉逗号
                return float(numbers[0].replace(',', ''))
            return None
        
        return salary_series.apply(extract_salary)
    
    def _clean_skills_list(self, skills_str: str) -> str:
        """清洗技能列表"""
        if pd.isna(skills_str):
            return ""
        
        skills_str = str(skills_str)
        # 移除多余的空格和特殊字符
        skills_str = re.sub(r'\s+', ' ', skills_str.strip())
        return skills_str
    
    def extract_skills(self, df: pd.DataFrame) -> pd.DataFrame:
        """从职位描述中提取技能"""
        print("\n开始技能提取...")
        
        # 常见技能关键词
        skill_keywords = {
            'Python': ['python', 'py', 'django', 'flask', 'pandas', 'numpy'],
            'JavaScript': ['javascript', 'js', 'node.js', 'react', 'angular', 'vue'],
            'Java': ['java', 'spring', 'hibernate', 'maven'],
            'SQL': ['sql', 'mysql', 'postgresql', 'oracle', 'sqlite'],
            'R': ['r programming', 'r language', 'rstudio'],
            'Excel': ['excel', 'microsoft excel', 'spreadsheet'],
            'Tableau': ['tableau', 'tableau desktop', 'tableau server'],
            'Power BI': ['power bi', 'powerbi', 'microsoft power bi'],
            'AWS': ['aws', 'amazon web services', 'ec2', 's3', 'lambda'],
            'Azure': ['azure', 'microsoft azure'],
            'Google Cloud': ['gcp', 'google cloud', 'google cloud platform'],
            'Docker': ['docker', 'containerization'],
            'Kubernetes': ['kubernetes', 'k8s'],
            'Git': ['git', 'github', 'gitlab', 'version control'],
            'Machine Learning': ['machine learning', 'ml', 'scikit-learn', 'tensorflow', 'pytorch'],
            'Data Analysis': ['data analysis', 'analytics', 'statistical analysis'],
            'Data Visualization': ['data visualization', 'visualization', 'charts', 'graphs'],
            'Project Management': ['project management', 'agile', 'scrum', 'jira']
        }
        
        def extract_skills_from_text(text):
            if pd.isna(text):
                return []
            
            text = str(text).lower()
            found_skills = []
            
            for skill, keywords in skill_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        found_skills.append(skill)
                        break
            
            return list(set(found_skills))  # 去重
        
        # 从技能列表和描述中提取技能
        if 'skills_list' in df.columns:
            df['extracted_skills'] = df['skills_list'].apply(
                lambda x: extract_skills_from_text(x) if pd.notna(x) else []
            )
        else:
            df['extracted_skills'] = [[]] * len(df)
        
        if 'description' in df.columns:
            df['description_skills'] = df['description'].apply(extract_skills_from_text)
            # 合并技能列表
            df['all_skills'] = df.apply(
                lambda row: list(set(row['extracted_skills'] + row['description_skills'])), 
                axis=1
            )
        else:
            df['all_skills'] = df['extracted_skills']
        
        # 统计技能
        all_skills = []
        for skills in df['all_skills']:
            all_skills.extend(skills)
        
        skill_counts = pd.Series(all_skills).value_counts()
        print(f"提取到 {len(skill_counts)} 种不同技能")
        print("前10个最常见技能:")
        for skill, count in skill_counts.head(10).items():
            print(f"  {skill}: {count} 次")
        
        return df
    
    def generate_summary_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """生成摘要报告"""
        print("\n生成摘要报告...")
        
        report = {
            'total_jobs': len(df),
            'unique_companies': df['company'].nunique() if 'company' in df.columns else 0,
            'salary_stats': {},
            'location_stats': {},
            'skill_stats': {}
        }
        
        # 薪资统计
        if 'salary_min' in df.columns and 'salary_max' in df.columns:
            valid_salaries = df[(df['salary_min'].notna()) & (df['salary_max'].notna())]
            if len(valid_salaries) > 0:
                report['salary_stats'] = {
                    'avg_min_salary': valid_salaries['salary_min'].mean(),
                    'avg_max_salary': valid_salaries['salary_max'].mean(),
                    'median_min_salary': valid_salaries['salary_min'].median(),
                    'median_max_salary': valid_salaries['salary_max'].median(),
                    'salary_range_count': len(valid_salaries)
                }
        
        # 位置统计
        if 'location' in df.columns:
            location_counts = df['location'].value_counts().head(10)
            report['location_stats'] = location_counts.to_dict()
        
        # 技能统计
        all_skills = []
        for skills in df['all_skills']:
            all_skills.extend(skills)
        
        if all_skills:
            skill_counts = pd.Series(all_skills).value_counts()
            report['skill_stats'] = skill_counts.head(20).to_dict()
        
        return report
    
    def save_results(self, df: pd.DataFrame, output_folder: str = "output"):
        """保存结果"""
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # 保存PA州数据
        pa_output_file = os.path.join(output_folder, "pa_jobs_cleaned.csv")
        df.to_csv(pa_output_file, index=False, encoding='utf-8-sig')
        print(f"\nPA州清洗后数据已保存到: {pa_output_file}")
        
        # 保存摘要报告
        report = self.generate_summary_report(df)
        report_file = os.path.join(output_folder, "pa_analysis_report.txt")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("PA州职位数据分析报告\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"总职位数: {report['total_jobs']}\n")
            f.write(f"唯一公司数: {report['unique_companies']}\n\n")
            
            if report['salary_stats']:
                f.write("薪资统计:\n")
                for key, value in report['salary_stats'].items():
                    f.write(f"  {key}: {value:.2f}\n")
                f.write("\n")
            
            if report['location_stats']:
                f.write("位置分布 (前10):\n")
                for location, count in report['location_stats'].items():
                    f.write(f"  {location}: {count}\n")
                f.write("\n")
            
            if report['skill_stats']:
                f.write("技能统计 (前20):\n")
                for skill, count in report['skill_stats'].items():
                    f.write(f"  {skill}: {count}\n")
        
        print(f"分析报告已保存到: {report_file}")
        
        return pa_output_file, report_file
    
    def run_full_analysis(self):
        """运行完整分析流程"""
        print("开始PA州职位数据完整分析...")
        print("=" * 60)
        
        try:
            # 1. 加载和合并CSV文件
            combined_df = self.load_and_combine_csvs()
            
            # 2. 筛选PA州数据
            pa_df = self.filter_pa_data(combined_df)
            
            # 3. 数据清洗
            cleaned_df = self.clean_data(pa_df)
            
            # 4. 技能提取
            final_df = self.extract_skills(cleaned_df)
            
            # 5. 保存结果
            output_file, report_file = self.save_results(final_df)
            
            print("\n" + "=" * 60)
            print("分析完成!")
            print(f"输出文件: {output_file}")
            print(f"报告文件: {report_file}")
            
            return final_df
            
        except Exception as e:
            print(f"分析过程中出现错误: {str(e)}")
            raise


def main():
    """主函数"""
    # 设置数据文件夹路径
    data_folder = "data/raw_data_project"
    
    # 创建处理器并运行分析
    processor = PADataProcessor(data_folder)
    result_df = processor.run_full_analysis()
    
    print(f"\n最终数据形状: {result_df.shape}")
    print("列名:", list(result_df.columns))
    
    return result_df


if __name__ == "__main__":
    result = main()
