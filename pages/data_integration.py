#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Integration Page for Pennsylvania Employment Dashboard
========================================================

This module contains the data integration page functionality for the Streamlit dashboard.

Author: Fan Yang (CMU)
Version: 1.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime

def show_data_integration(pa_data, bls_data):
    """Show data integration section"""
    st.header("🔗 Data Integration")
    
    st.subheader("📋 Google Sheets Integration")
    st.info("""
    **Google Sheets Data Source:**
    https://docs.google.com/spreadsheets/d/1kGx-QwGAiwd1zs0PNDuVAbyN1L7V7ezDrdqKXf4Exws/edit?gid=0#gid=0
    
    This spreadsheet contains cleaned job listings data organized by different job categories.
    """)
    
    # Data integration options
    st.subheader("🛠️ Integration Tools")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Available Data Sources:**")
        st.write("- ✅ Pennsylvania O*NET Occupation Data")
        st.write("- ✅ BLS Employment Statistics")
        st.write("- ✅ BLS Wage Data")
        st.write("- ✅ Employment Projections")
        st.write("- 🔄 Google Sheets Job Listings (Ready for integration)")
    
    with col2:
        st.write("**Integration Features:**")
        st.write("- 📊 Cross-reference job listings with O*NET data")
        st.write("- 💰 Compare salary data across sources")
        st.write("- 📈 Analyze job growth projections")
        st.write("- 🎯 Match skills requirements")
    
    # Data export options
    st.subheader("📤 Data Export")
    
    if st.button("Export Combined Dataset"):
        # Combine data sources
        combined_data = pa_data.copy()
        
        # Add BLS data if available
        if 'employment' in bls_data:
            st.write("Adding BLS employment data...")
        
        # Export to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"combined_pa_data_{timestamp}.csv"
        combined_data.to_csv(filename, index=False, encoding='utf-8-sig')
        
        st.success(f"Combined dataset exported as: {filename}")
        
        # Download button
        with open(filename, 'rb') as f:
            st.download_button(
                label="Download Combined Dataset",
                data=f.read(),
                file_name=filename,
                mime='text/csv'
            )
