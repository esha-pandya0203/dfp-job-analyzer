#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skills Analysis Page for Pennsylvania Employment Dashboard
========================================================

This module contains the skills analysis page functionality for the Streamlit dashboard.

Author: Fan Yang (CMU)
Version: 1.0
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import re
from collections import Counter

def analyze_skills(df):
    """Analyze skills data"""
    all_tech_skills = []
    
    # Technology skills only (general skills column is empty)
    if 'technology_skills' in df.columns:
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
    
    return all_tech_skills, []  # 返回空列表作为general_skills

def show_skills_analysis(pa_data):
    """Show skills analysis"""
    st.header("🛠️ Skills Analysis")
    
    # Analyze skills
    tech_skills, general_skills = analyze_skills(pa_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💻 Technology Skills")
        if tech_skills:
            tech_skill_counts = Counter(tech_skills)
            top_tech_skills = dict(tech_skill_counts.most_common(15))
            
            fig = px.bar(
                x=list(top_tech_skills.values()),
                y=list(top_tech_skills.keys()),
                orientation='h',
                title="Top 15 Technology Skills",
                labels={'x': 'Frequency', 'y': 'Skill'}
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No technology skills data available")
    
    with col2:
        st.subheader("📊 Skills Summary")
        if tech_skills:
            st.write(f"**Total Technology Skills Found:** {len(set(tech_skills))}")
            st.write(f"**Total Skill Mentions:** {len(tech_skills)}")
            
            # Show top 5 skills as text
            tech_skill_counts = Counter(tech_skills)
            st.write("**Top 5 Skills:**")
            for i, (skill, count) in enumerate(tech_skill_counts.most_common(5), 1):
                st.write(f"{i}. {skill}: {count} times")
        else:
            st.info("No technology skills data available")
    
    # Skills by occupation family
    if 'technology_skills' in pa_data.columns:
        st.subheader("📊 Technology Skills by Occupation Family")
        
        family_tech_skills = {}
        for family in pa_data['occupation_family'].unique():
            family_data = pa_data[pa_data['occupation_family'] == family]
            family_skills = []
            
            for skills in family_data['technology_skills'].dropna():
                if isinstance(skills, str):
                    skill_list = re.split(r'[,;]', skills)
                    family_skills.extend([skill.strip() for skill in skill_list if skill.strip()])
            
            if family_skills:
                family_tech_skills[family] = Counter(family_skills).most_common(5)
        
        # Create heatmap data
        all_skills = set()
        for skills_list in family_tech_skills.values():
            all_skills.update([skill for skill, _ in skills_list])
        
        heatmap_data = []
        for family, skills_list in family_tech_skills.items():
            skill_dict = dict(skills_list)
            row = [skill_dict.get(skill, 0) for skill in all_skills]
            heatmap_data.append(row)
        
        if heatmap_data:
            fig = px.imshow(
                heatmap_data,
                labels=dict(x="Technology Skills", y="Occupation Family", color="Frequency"),
                x=list(all_skills),
                y=list(family_tech_skills.keys()),
                title="Technology Skills Heatmap by Occupation Family"
            )
            st.plotly_chart(fig, width='stretch')
