#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据文件规模
"""

import pandas as pd
import os
import glob

def check_data_size():
    print("检查所有数据文件的规模...")
    print("=" * 50)
    
    # 数据文件夹路径
    data_folder = "data/raw_data_project"
    
    # 获取所有CSV文件
    csv_files = glob.glob(os.path.join(data_folder, "*.csv"))
    
    print(f"找到 {len(csv_files)} 个CSV文件:")
    print()
    
    total_rows = 0
    file_info = []
    
    for file_path in csv_files:
        try:
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            
            # 读取文件获取行数
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
            print(f"   行数: {rows:,}")
            print(f"   列数: {len(df.columns)}")
            print(f"   大小: {file_size_mb:.2f} MB")
            print(f"   列名: {list(df.columns)[:5]}..." if len(df.columns) > 5 else f"   列名: {list(df.columns)}")
            print()
            
        except Exception as e:
            print(f"❌ 读取文件 {os.path.basename(file_path)} 时出错: {e}")
            print()
    
    # 总结
    print("=" * 50)
    print(f"📊 数据总结:")
    print(f"   总文件数: {len(csv_files)}")
    print(f"   总行数: {total_rows:,}")
    print(f"   最大文件: {max(file_info, key=lambda x: x['rows'])['filename']}")
    print(f"   最大文件行数: {max(file_info, key=lambda x: x['rows'])['rows']:,}")
    
    # 检查PA州数据
    print("\n" + "=" * 50)
    print("🔍 检查PA州数据:")
    
    # 检查专门的PA州文件
    pa_file = os.path.join(data_folder, "pennsylvania_occupations_20250924_105620.csv")
    if os.path.exists(pa_file):
        pa_df = pd.read_csv(pa_file)
        print(f"   PA州专门文件: {len(pa_df)} 个职位")
        print(f"   职位族: {pa_df['occupation_family'].unique()}")
    
    # 检查大文件中是否有PA州数据
    largest_file = max(file_info, key=lambda x: x['rows'])
    print(f"\n📈 最大的文件 ({largest_file['filename']}) 分析:")
    
    if largest_file['rows'] > 10000:  # 如果文件很大，只读取一部分
        print("   文件太大，读取前1000行进行分析...")
        df_sample = pd.read_csv(os.path.join(data_folder, largest_file['filename']), nrows=1000)
    else:
        df_sample = pd.read_csv(os.path.join(data_folder, largest_file['filename']))
    
    # 检查是否有位置信息
    location_keywords = ['location', 'state', 'city', 'address']
    location_cols = []
    
    for col in df_sample.columns:
        if any(keyword in col.lower() for keyword in location_keywords):
            location_cols.append(col)
    
    print(f"   位置相关列: {location_cols}")
    
    if location_cols:
        print("   检查是否包含PA州数据...")
        for col in location_cols:
            if col in df_sample.columns:
                pa_matches = df_sample[col].astype(str).str.contains('PA|Pennsylvania', case=False, na=False).sum()
                print(f"     {col}: {pa_matches} 行包含PA关键词")
    
    return file_info

if __name__ == "__main__":
    file_info = check_data_size()
