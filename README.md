# US Employment Dashboard

A comprehensive web scraping and data analysis project for Pennsylvania employment data, featuring an interactive Streamlit dashboard.

## 📁 Project Structure

```
Project_web_scraping_FY/
├── app.py                          # Main Streamlit application
├── modules/                        # Core scraping and analysis modules
│   ├── config.py                   # Configuration settings
│   ├── data_analyzer.py            # Data analysis tools
│   ├── onet_scraper.py             # O*NET scraper
│   └── pennsylvania_scraper.py     # Pennsylvania-specific scraper
├── pages/                          # Streamlit page modules
│   ├── overview.py                 # Dashboard overview
│   ├── job_search.py               # Job search functionality
│   ├── occupation_analysis.py      # Occupation analysis
│   ├── skills_analysis.py          # Skills analysis
│   ├── salary_analysis.py          # Salary analysis
│   ├── bls_statistics.py           # BLS statistics
│   └── data_integration.py         # Data integration
├── utils/                          # Utility functions
│   ├── data_loader.py              # Data loading utilities
│   ├── job_data_loader.py          # Job data loader
│   ├── job_title_mapping.py        # BLS SOC code mapping
│   ├── mock_job_data.py            # Mock data generator
│   ├── analyze_pa_data_fixed.py    # PA data analysis
│   ├── check_data_size.py          # Data validation
│   └── pa_data_processor.py        # Data processing
├── data/                           # Data files
│   ├── mock_job_data.csv           # Mock job data
│   └── raw_data_project/           # Raw data files
│       ├── pennsylvania_all_occupations_*.csv
│       ├── Annual_mean_wage_*.csv
│       ├── Civilian_Employment_*.csv
│       └── other BLS data files
├── output/                         # Analysis results
│   ├── pa_jobs_analysis.csv
│   ├── pa_salary_analysis.csv
│   ├── pa_skills_summary.csv
│   └── project_summary.json
├── scripts/                        # Run scripts
│   ├── run_dashboard.py            # Dashboard launcher
│   ├── start_dashboard.bat         # Windows batch script
│   └── start_dashboard.ps1         # PowerShell script
├── config/                         # Configuration files
│   ├── google_sheets_integration.py
│   └── project_integration.py
├── docs/                           # Documentation
│   ├── README.md                   # Detailed documentation
│   └── final_project_rubric.docx   # Project requirements
└── legacy/                         # Legacy files
    └── fan-yang/                   # Original fan-yang directory
        ├── CSV_Columns_Explanation.txt
        ├── LICENSE
        ├── README.md
        └── requirements.txt
```

## 🚀 Quick Start

### Option 1: Using Batch Script (Windows)
```bash
scripts/start_dashboard.bat
```

### Option 2: Using PowerShell Script
```bash
scripts/start_dashboard.ps1
```

### Option 3: Direct Streamlit Command
```bash
streamlit run app.py
```

## 📊 Features

- **Job Search**: Search for specific job titles with market analysis
- **Occupation Analysis**: Comprehensive occupation data analysis
- **Skills Analysis**: Technology skills breakdown and trends
- **Salary Analysis**: Salary range analysis and comparisons
- **BLS Statistics**: Bureau of Labor Statistics integration
- **Data Integration**: Multi-source data integration

## 🛠️ Data Sources

- **O*NET Online**: 997+ occupation profiles
- **BLS API**: Labor statistics and employment data
- **Google Sheets**: Team-collected job listings
- **Pennsylvania-specific**: State employment data

## 📈 Key Metrics

- **Data Completeness**: 95%+ for most fields
- **Occupation Coverage**: 997+ occupations
- **Technology Skills**: Comprehensive skill mapping
- **Salary Data**: Median salary information
- **Market Trends**: Employment projections and growth

## 🔧 Technical Stack

- **Python**: Core programming language
- **Streamlit**: Web dashboard framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **Requests**: API integration
- **BeautifulSoup**: Web scraping

## 📝 Usage

1. **Launch Dashboard**: Use any of the quick start options above
2. **Navigate**: Use the sidebar to select different analysis sections
3. **Search Jobs**: Enter job titles in the Job Search page
4. **Explore Data**: Browse through different analysis views
5. **Export Results**: Download analysis results from the output directory

## 🎯 Project Goals

This project aims to provide comprehensive employment market analysis for Pennsylvania, integrating multiple data sources to offer insights into:

- Job market trends
- Salary expectations
- Required skills
- Employment projections
- Regional analysis

## 📞 Support

For questions or issues, please refer to the documentation in the `docs/` directory or check the legacy files in `legacy/fan-yang/` for additional context.
