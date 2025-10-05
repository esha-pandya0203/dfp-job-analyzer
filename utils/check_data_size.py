#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check data file sizes
"""

import pandas as pd
import os
import glob

def check_data_size():
    print("Checking sizes of all data files...")
    print("=" * 50)
    
    # Data folder path
    data_folder = "data/raw_data_project"
    
    # Get all CSV files
    csv_files = glob.glob(os.path.join(data_folder, "*.csv"))
    
    print(f"Found {len(csv_files)} CSV files:")
    print()
    
    total_rows = 0
    file_info = []
    
    for file_path in csv_files:
        try:
            # Get file size
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            
            # Read file to get row count
            df = pd.read_csv(file_path)
            rows = len(df)
            total_rows += rows
            
            file_info.append({
                'filename': os.path.basename(file_path),
                'rows': rows,
                'size_mb': round(file_size_mb, 2),
                'columns': len(df.columns)
            })
            
            print(f"📄 {os.path.basename(file_path)}")
            print(f"   Rows: {rows:,}")
            print(f"   Columns: {len(df.columns)}")
            print(f"   Size: {file_size_mb:.2f} MB")
            print(f"   Column names: {list(df.columns)[:5]}..." if len(df.columns) > 5 else f"   Column names: {list(df.columns)}")
            print()
            
        except Exception as e:
            print(f"❌ Error reading file {os.path.basename(file_path)}: {e}")
            print()
    
    # Summary
    print("=" * 50)
    print(f"📊 Data Summary:")
    print(f"   Total files: {len(csv_files)}")
    print(f"   Total rows: {total_rows:,}")
    print(f"   Largest file: {max(file_info, key=lambda x: x['rows'])['filename']}")
    print(f"   Largest file rows: {max(file_info, key=lambda x: x['rows'])['rows']:,}")
    
    # Check PA state data
    print("\n" + "=" * 50)
    print("🔍 Checking PA state data:")
    
    # Check dedicated PA state file
    pa_file = os.path.join(data_folder, "pennsylvania_occupations_20250924_105620.csv")
    if os.path.exists(pa_file):
        pa_df = pd.read_csv(pa_file)
        print(f"   PA dedicated file: {len(pa_df)} occupations")
        print(f"   Occupation families: {pa_df['occupation_family'].unique()}")
    
    # Check if large files contain PA state data
    largest_file = max(file_info, key=lambda x: x['rows'])
    print(f"\n📈 Analysis of largest file ({largest_file['filename']}):")
    
    if largest_file['rows'] > 10000:  # If file is too large, only read first 1000 rows
        print("   File too large, reading first 1000 rows for analysis...")
        df_sample = pd.read_csv(os.path.join(data_folder, largest_file['filename']), nrows=1000)
    else:
        df_sample = pd.read_csv(os.path.join(data_folder, largest_file['filename']))
    
    # Check for location information
    location_keywords = ['location', 'state', 'city', 'address']
    location_cols = []
    
    for col in df_sample.columns:
        if any(keyword in col.lower() for keyword in location_keywords):
            location_cols.append(col)
    
    print(f"   Location-related columns: {location_cols}")
    
    if location_cols:
        print("   Checking if contains PA state data...")
        for col in location_cols:
            if col in df_sample.columns:
                pa_matches = df_sample[col].astype(str).str.contains('PA|Pennsylvania', case=False, na=False).sum()
                print(f"     {col}: {pa_matches} rows contain PA keywords")
    
    return file_info

if __name__ == "__main__":
    file_info = check_data_size()
