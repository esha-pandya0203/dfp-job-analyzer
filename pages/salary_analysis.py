#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Salary Analysis Page for Pennsylvania Employment Dashboard
========================================================

This module contains the salary analysis page functionality for the Streamlit dashboard.

Author: Fan Yang (CMU)
Version: 1.0
"""

import streamlit as st
import pandas as pd
import plotly.express as px

def show_salary_analysis(pa_data):
    """Show salary analysis"""
    st.header("💰 Salary Analysis")
    
    if 'salary_median_clean' not in pa_data.columns:
        st.error("No salary data available")
        return
    
    valid_salaries = pa_data['salary_median_clean'].dropna()
    
    if len(valid_salaries) == 0:
        st.error("No valid salary data found")
        return
    
    # Salary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Mean Salary", f"${valid_salaries.mean():,.2f}")
    with col2:
        st.metric("Median Salary", f"${valid_salaries.median():,.2f}")
    with col3:
        st.metric("Max Salary", f"${valid_salaries.max():,.2f}")
    with col4:
        st.metric("Min Salary", f"${valid_salaries.min():,.2f}")
    
    # Salary distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Salary Distribution")
        fig = px.histogram(
            valid_salaries,
            nbins=20,
            title="Salary Distribution",
            labels={'x': 'Salary ($/hour)', 'y': 'Count'}
        )
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.subheader("📈 Salary by Occupation Family")
        salary_by_family = pa_data.groupby('occupation_family')['salary_median_clean'].mean().sort_values(ascending=False)
        
        fig = px.bar(
            x=salary_by_family.values,
            y=salary_by_family.index,
            orientation='h',
            title="Average Salary by Occupation Family",
            labels={'x': 'Average Salary ($/hour)', 'y': 'Occupation Family'}
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, width='stretch')
    
    # Salary ranges
    st.subheader("🎯 Salary Range Analysis")
    
    salary_ranges = [
        (0, 30, "Low Salary (<$30/hr)"),
        (30, 50, "Medium Salary ($30-$50/hr)"),
        (50, 70, "High Salary ($50-$70/hr)"),
        (70, float('inf'), "Very High Salary (>$70/hr)")
    ]
    
    range_data = []
    for min_sal, max_sal, label in salary_ranges:
        count = len(valid_salaries[(valid_salaries >= min_sal) & (valid_salaries < max_sal)])
        percentage = count / len(valid_salaries) * 100
        range_data.append({
            'Range': label,
            'Count': count,
            'Percentage': percentage
        })
    
    range_df = pd.DataFrame(range_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            range_df,
            values='Count',
            names='Range',
            title="Salary Range Distribution"
        )
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.dataframe(range_df, width='stretch')
