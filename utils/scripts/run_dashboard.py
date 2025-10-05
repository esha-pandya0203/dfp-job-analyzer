#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pennsylvania Employment Dashboard Launcher
==========================================

This script launches the Streamlit dashboard for Pennsylvania employment analysis.

Author: Fan Yang (CMU)
Version: 1.0
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit',
        'pandas',
        'numpy',
        'plotly',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            # Try importing the package
            __import__(package)
            print(f"[OK] {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"[MISSING] {package}")
    
    if missing_packages:
        print(f"\n[MISSING] {len(missing_packages)} required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n[INFO] Note: Make sure you're using the correct Python environment")
        print("[INFO] If using virtual environment, activate it first:")
        print("   .venv\\Scripts\\activate  (Windows)")
        print("   source .venv/bin/activate  (Linux/Mac)")
        print(f"\n[INSTALL] Then install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("[OK] All required packages are installed")
    return True

def check_data_files():
    """Check if required data files exist"""
    required_files = [
        "data/raw_data_project/pennsylvania_all_occupations_20250927_201529.csv"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("[MISSING] Missing required data files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\n[INFO] Please ensure all data files are in the correct location")
        return False
    
    return True

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    print("Launching Pennsylvania Employment Dashboard...")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check data files
    if not check_data_files():
        return False
    
    print("All dependencies and data files are available")
    print("Starting Streamlit dashboard...")
    print("The dashboard will open in your default web browser")
    print("If it doesn't open automatically, go to: http://localhost:8501")
    print("\n" + "=" * 60)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\nDashboard stopped by user")
    except Exception as e:
        print(f"Error launching dashboard: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("Pennsylvania Employment Dashboard Launcher")
    print("=" * 60)
    
    success = launch_dashboard()
    
    if success:
        print("Dashboard launched successfully")
    else:
        print("Failed to launch dashboard")
        sys.exit(1)

if __name__ == "__main__":
    main()

