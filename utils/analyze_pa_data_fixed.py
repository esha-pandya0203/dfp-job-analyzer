#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PA州职位数据专项分析脚本（修复版）
针对pennsylvania_occupations_20250924_105620.csv文件
"""

import pandas as pd
import numpy as np
import os
import re
import sys
from collections import Counter

# Fix Windows console encoding
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def clean_salary_data(salary_str):
    """清洗薪资数据"""
    if pd.isna(salary_str):
        return None
    
    salary_str = str(salary_str)
    
    # 如果包含多个薪资值，取第一个
    if '$' in salary_str:
        # 提取所有薪资值
        salaries = re.findall(r'\$(\d+(?:\.\d{2})?)', salary_str)
        if salaries:
            # 返回第一个薪资值
            return float(salaries[0])
    
    # 尝试直接转换
    try:
        return float(salary_str)
    except:
        return None

def analyze_pa_data():
    """分析PA州职位数据"""
    print("开始分析PA州职位数据...")
    print("=" * 60)
    
    # 读取PA州数据文件
    data_folder = "data/raw_data_project"
    pa_file = os.path.join(data_folder, "pennsylvania_all_occupations_20250927_201529.csv")

    if not os.path.exists(pa_file):
        print(f"错误: 找不到文件 {pa_file}")
        return None
    
    # 读取数据
    print(f"读取文件: {os.path.basename(pa_file)}")
    df = pd.read_csv(pa_file)
    print(f"数据形状: {df.shape}")
    print(f"列名: {list(df.columns)}")
    
    # 清洗薪资数据
    if 'salary_median' in df.columns:
        print(f"\n清洗薪资数据...")
        print(f"原始薪资数据示例: {df['salary_median'].iloc[0]}")
        df['salary_median_clean'] = df['salary_median'].apply(clean_salary_data)
        valid_salaries = df['salary_median_clean'].dropna()
        print(f"成功清洗的薪资数据: {len(valid_salaries)} 个")
    
    # 基本信息统计
    print(f"\n基本信息:")
    print(f"  总职位数: {len(df)}")
    print(f"  唯一职位族: {df['occupation_family'].nunique()}")
    
    # 薪资分析
    print(f"\n薪资分析:")
    if 'salary_median_clean' in df.columns:
        salary_data = df['salary_median_clean'].dropna()
        if len(salary_data) > 0:
            print(f"  有薪资数据的职位: {len(salary_data)}")
            print(f"  平均薪资: ${salary_data.mean():,.2f}")
            print(f"  薪资中位数: ${salary_data.median():,.2f}")
            print(f"  最高薪资: ${salary_data.max():,.2f}")
            print(f"  最低薪资: ${salary_data.min():,.2f}")
            
            # 薪资分布
            print(f"\n薪资分布:")
            salary_ranges = [
                (0, 30, "低薪资 (<$30/hr)"),
                (30, 50, "中等薪资 ($30-$50/hr)"),
                (50, 70, "高薪资 ($50-$70/hr)"),
                (70, float('inf'), "超高薪资 (>$70/hr)")
            ]
            
            for min_sal, max_sal, label in salary_ranges:
                count = len(salary_data[(salary_data >= min_sal) & (salary_data < max_sal)])
                percentage = count / len(salary_data) * 100
                print(f"  {label}: {count} 个职位 ({percentage:.1f}%)")
    
    # 职位族分析
    print(f"\n职位族分析:")
    family_counts = df['occupation_family'].value_counts()
    print(f"职位族分布:")
    for family, count in family_counts.items():
        print(f"  {family}: {count} 个职位")
    
    # 技能分析
    print(f"\n技能分析:")
    
    # 分析technology_skills列
    if 'technology_skills' in df.columns:
        all_tech_skills = []
        for skills in df['technology_skills'].dropna():
            if isinstance(skills, str):
                # 清理数据：移除方括号和引号
                skills_clean = skills.strip()
                # 移除开头的 [ 和结尾的 ]
                if skills_clean.startswith('[') and skills_clean.endswith(']'):
                    skills_clean = skills_clean[1:-1]
                
                # 分割技能（用逗号分隔）
                skill_list = re.split(r',', skills_clean)
                for skill in skill_list:
                    skill = skill.strip()
                    # 移除引号
                    if skill.startswith("'") and skill.endswith("'"):
                        skill = skill[1:-1]
                    elif skill.startswith('"') and skill.endswith('"'):
                        skill = skill[1:-1]
                    
                    # 只添加非空的技能名称
                    if skill and skill not in ['', '[]', 'None']:
                        all_tech_skills.append(skill)
        
        if all_tech_skills:
            skill_counts = Counter(all_tech_skills)
            print(f"技术技能统计 (前15个):")
            for skill, count in skill_counts.most_common(15):
                print(f"  {skill}: {count} 次")
    
    # 教育水平分析
    if 'education_level' in df.columns:
        print(f"\n教育水平要求:")
        edu_counts = df['education_level'].value_counts()
        for level, count in edu_counts.items():
            print(f"  {level}: {count} 个职位")
    
    # 工作增长分析已删除（数据为空）
    
    # 创建输出文件夹
    output_folder = "output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 保存分析结果
    output_file = os.path.join(output_folder, "pa_jobs_analysis.csv")
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n分析结果已保存到: {output_file}")
    
    # 生成技能统计文件
    if 'technology_skills' in df.columns and 'skills' in df.columns:
        skills_summary = []
        
        # 技术技能统计
        if all_tech_skills:
            tech_skill_counts = Counter(all_tech_skills)
            for skill, count in tech_skill_counts.most_common(20):
                skills_summary.append({
                    'skill_type': 'Technology',
                    'skill_name': skill,
                    'frequency': count,
                    'percentage': count / len(df) * 100
                })
        
        # 通用技能统计已删除（数据为空）
        
        if skills_summary:
            skills_df = pd.DataFrame(skills_summary)
            skills_file = os.path.join(output_folder, "pa_skills_summary.csv")
            skills_df.to_csv(skills_file, index=False, encoding='utf-8-sig')
            print(f"技能统计已保存到: {skills_file}")
    
    # 生成薪资分析文件
    if 'salary_median_clean' in df.columns:
        salary_analysis = df[['title', 'occupation_family', 'salary_median_clean', 'job_growth']].copy()
        salary_analysis = salary_analysis.sort_values('salary_median_clean', ascending=False)
        salary_file = os.path.join(output_folder, "pa_salary_analysis.csv")
        salary_analysis.to_csv(salary_file, index=False, encoding='utf-8-sig')
        print(f"薪资分析已保存到: {salary_file}")
    
    # 生成详细的职位报告
    print(f"\n生成详细职位报告...")
    
    # 按薪资排序显示前10个职位
    if 'salary_median_clean' in df.columns:
        top_jobs = df.nlargest(10, 'salary_median_clean')[['title', 'salary_median_clean', 'job_growth', 'occupation_family']]
        print(f"\n薪资最高的10个职位:")
        for idx, row in top_jobs.iterrows():
            print(f"  {row['title']}: ${row['salary_median_clean']:.2f}/hr (增长: {row['job_growth']:.1f}%)")
    
    print(f"\n分析完成!")
    print(f"总共分析了 {len(df)} 个PA州职位")
    
    return df

if __name__ == "__main__":
    result = analyze_pa_data()
