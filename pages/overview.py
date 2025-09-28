#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Overview Page for Pennsylvania Employment Dashboard
=================================================

This module contains the overview page functionality for the Streamlit dashboard.

Author: Fan Yang (CMU)
Version: 1.0
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show_overview(pa_data, bls_data):
    """Show overview dashboard"""
    st.header("📈 Pennsylvania Employment Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Occupations",
            value=len(pa_data),
            delta=f"{pa_data['occupation_family'].nunique()} families"
        )
    
    with col2:
        valid_salaries = pa_data['salary_median_clean'].dropna()
        if len(valid_salaries) > 0:
            avg_salary = valid_salaries.mean()
            st.metric(
                label="Average Salary",
                value=f"${avg_salary:,.0f}",
                delta="per hour"
            )
        else:
            st.metric("Average Salary", "N/A")
    
    with col3:
        if 'job_growth' in pa_data.columns:
            growth_data = pa_data['job_growth'].dropna()
            if len(growth_data) > 0:
                avg_growth = growth_data.mean()
                st.metric(
                    label="Average Job Growth",
                    value=f"{avg_growth:.1f}%",
                    delta="projected"
                )
            else:
                st.metric("Average Job Growth", "No Data", delta="N/A")
        else:
            st.metric("Average Job Growth", "No Data", delta="N/A")
    
    with col4:
        if 'pa_cities_mentioned' in pa_data.columns:
            # Parse string format lists and count cities
            def count_cities(city_str):
                if pd.isna(city_str):
                    return 0
                if isinstance(city_str, str):
                    # Remove brackets and quotes, then split by comma
                    city_str = city_str.strip("[]").replace("'", "").replace('"', "")
                    cities = [city.strip() for city in city_str.split(',') if city.strip()]
                    return len(cities)
                return 0
            
            cities_mentioned = pa_data['pa_cities_mentioned'].apply(count_cities).sum()
            st.metric(
                label="City Mentions",
                value=cities_mentioned,
                delta="total references"
            )
        else:
            st.metric("City Mentions", "N/A")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Occupation Family Distribution")
        family_counts = pa_data['occupation_family'].value_counts()
        
        fig = px.pie(
            values=family_counts.values,
            names=family_counts.index,
            title="Distribution by Occupation Family"
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.subheader("💰 Salary Distribution")
        valid_salaries = pa_data['salary_median_clean'].dropna()
        
        if len(valid_salaries) > 0:
            fig = px.histogram(
                valid_salaries,
                nbins=20,
                title="Salary Distribution",
                labels={'x': 'Salary ($/hour)', 'y': 'Count'}
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No salary data available")
    
    # Data summary
    st.subheader("📋 Data Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Data Completeness:**")
        completeness = {
            'Descriptions': len(pa_data[pa_data['description'].str.len() > 0]),
            'Technology Skills': len(pa_data[pa_data['technology_skills'].apply(lambda x: len(str(x).strip()) > 2 if pd.notna(x) else False)]),
            'Education Info': len(pa_data[pa_data['education_level'].str.len() > 0]),
            'Salary Data': len(pa_data['salary_median_clean'].dropna())
        }
        
        for field, count in completeness.items():
            percentage = (count / len(pa_data)) * 100
            st.write(f"- {field}: {count}/{len(pa_data)} ({percentage:.1f}%)")
    
    with col2:
        st.write("**Top Occupation Families:**")
        top_families = pa_data['occupation_family'].value_counts().head(5)
        for family, count in top_families.items():
            st.write(f"- {family}: {count} occupations")
