#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Occupation Analysis Page for Pennsylvania Employment Dashboard
============================================================

This module contains the occupation analysis page functionality for the Streamlit dashboard.

Author: Fan Yang (CMU)
Version: 1.0
"""

import streamlit as st
import pandas as pd
import plotly.express as px

def show_occupation_analysis(pa_data):
    """Show occupation analysis"""
    st.header("👔 Occupation Analysis")
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        selected_family = st.selectbox(
            "Select Occupation Family",
            ["All"] + list(pa_data['occupation_family'].unique())
        )
    
    with col2:
        min_salary = st.slider(
            "Minimum Salary ($/hour)",
            min_value=0,
            max_value=200,
            value=0,
            step=5
        )
    
    # Filter data
    filtered_data = pa_data.copy()
    
    if selected_family != "All":
        filtered_data = filtered_data[filtered_data['occupation_family'] == selected_family]
    
    if 'salary_median_clean' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['salary_median_clean'] >= min_salary]
    
    st.write(f"Showing {len(filtered_data)} occupations")
    
    # Occupation table
    display_columns = ['title', 'occupation_family', 'salary_median_clean']
    available_columns = [col for col in display_columns if col in filtered_data.columns]
    
    if available_columns:
        st.subheader("📋 Occupation Details")
        st.dataframe(
            filtered_data[available_columns].sort_values(
                'salary_median_clean', 
                ascending=False, 
                na_position='last'
            ),
            width='stretch'
        )
    
    # Top occupations by salary
    if 'salary_median_clean' in filtered_data.columns:
        st.subheader("💎 Top 10 Highest Paying Occupations")
        top_jobs = filtered_data.nlargest(10, 'salary_median_clean')
        
        fig = px.bar(
            top_jobs,
            x='salary_median_clean',
            y='title',
            orientation='h',
            title="Top 10 Highest Paying Occupations",
            labels={'salary_median_clean': 'Salary ($/hour)', 'title': 'Occupation'}
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, width='stretch')
