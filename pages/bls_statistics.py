#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BLS Statistics Page for Pennsylvania Employment Dashboard
=======================================================

This module contains the BLS statistics page functionality for the Streamlit dashboard.

Author: Fan Yang (CMU)
Version: 1.0
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def show_bls_statistics(bls_data):
    """Show BLS statistics"""
    st.header("📊 Bureau of Labor Statistics")
    
    if not bls_data:
        st.error("No BLS data available")
        return
    
    # Employment data with visualization
    if 'employment' in bls_data:
        st.subheader("👥 Employment Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.dataframe(bls_data['employment'], width='stretch')
        
        with col2:
            # Create time series chart
            df_emp = bls_data['employment'].copy()
            if 'Date' in df_emp.columns and 'Value' in df_emp.columns:
                # Use Date column for x-axis and Value column for y-axis
                fig = px.line(df_emp, x='Date', y='Value', 
                            title="Employment Trends Over Time",
                            labels={'Date': 'Date', 'Value': 'Employment (Thousands)'})
                st.plotly_chart(fig, width='stretch')
            elif 'Year' in df_emp.columns and 'Value' in df_emp.columns:
                # Fallback to Year if Date not available
                fig = px.line(df_emp, x='Year', y='Value', 
                            title="Employment Trends Over Time",
                            labels={'Year': 'Year', 'Value': 'Employment (Thousands)'})
                st.plotly_chart(fig, width='stretch')
        
        # Download button for employment data
        csv_emp = bls_data['employment'].to_csv(index=False)
        st.download_button(
            label="📥 Download Employment Data (CSV)",
            data=csv_emp,
            file_name="employment_statistics.csv",
            mime="text/csv"
        )
    
    # Unemployment data with visualization
    if 'unemployment' in bls_data:
        st.subheader("📉 Unemployment Rate")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.dataframe(bls_data['unemployment'], width='stretch')
        
        with col2:
            # Create time series chart
            df_unemp = bls_data['unemployment'].copy()
            if 'Date' in df_unemp.columns and 'Value' in df_unemp.columns:
                # Use Date column for x-axis and Value column for y-axis
                fig = px.line(df_unemp, x='Date', y='Value', 
                            title="Unemployment Rate Trends Over Time",
                            labels={'Date': 'Date', 'Value': 'Unemployment Rate (%)'})
                st.plotly_chart(fig, width='stretch')
            elif 'Year' in df_unemp.columns and 'Value' in df_unemp.columns:
                # Fallback to Year if Date not available
                fig = px.line(df_unemp, x='Year', y='Value', 
                            title="Unemployment Rate Trends Over Time",
                            labels={'Year': 'Year', 'Value': 'Unemployment Rate (%)'})
                st.plotly_chart(fig, width='stretch')
        
        # Download button for unemployment data
        csv_unemp = bls_data['unemployment'].to_csv(index=False)
        st.download_button(
            label="📥 Download Unemployment Data (CSV)",
            data=csv_unemp,
            file_name="unemployment_statistics.csv",
            mime="text/csv"
        )
    
    # Wage data with visualization
    if 'wage_analysts' in bls_data:
        st.subheader("💰 Computer and Information Analysts Wages")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.dataframe(bls_data['wage_analysts'], width='stretch')
        
        with col2:
            # Create time series chart
            df_wage = bls_data['wage_analysts'].copy()
            if 'Year' in df_wage.columns and 'Value' in df_wage.columns:
                # Use Year column for x-axis and Value column for y-axis
                fig = px.line(df_wage, x='Year', y='Value', 
                            title="Wage Trends Over Time",
                            labels={'Year': 'Year', 'Value': 'Annual Wage ($)'})
                st.plotly_chart(fig, width='stretch')
            elif 'Date' in df_wage.columns and 'Value' in df_wage.columns:
                # Fallback to Date if available
                fig = px.line(df_wage, x='Date', y='Value', 
                            title="Wage Trends Over Time",
                            labels={'Date': 'Date', 'Value': 'Wage ($)'})
                st.plotly_chart(fig, width='stretch')
        
        # Download button for wage data
        csv_wage = bls_data['wage_analysts'].to_csv(index=False)
        st.download_button(
            label="📥 Download Wage Data (CSV)",
            data=csv_wage,
            file_name="wage_statistics.csv",
            mime="text/csv"
        )
    
    # Projections
    if 'projections' in bls_data:
        st.subheader("🔮 Employment Projections")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.dataframe(bls_data['projections'], width='stretch')
        
        with col2:
            # Create projection chart
            df_proj = bls_data['projections'].copy()
            numeric_cols = df_proj.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) > 0:
                fig = px.bar(df_proj, x=df_proj.columns[0], y=numeric_cols[0], 
                           title="Employment Projections")
                st.plotly_chart(fig, use_container_width=True)
        
        # Download button for projections data
        csv_proj = bls_data['projections'].to_csv(index=False)
        st.download_button(
            label="📥 Download Projections Data (CSV)",
            data=csv_proj,
            file_name="employment_projections.csv",
            mime="text/csv"
        )
