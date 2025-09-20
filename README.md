# Job Market & Skills Analyzer

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

### Project Overview

**Job Market & Skills Analyzer** is a comprehensive Python application designed to help students and job seekers understand the most valuable technical skills, tools, and courses in today's job market. By integrating real-time job postings, labor statistics, and salary data, it addresses the problem of fragmented, outdated, or anecdotal career planning information.

### 🎯 Project Goals

- **Data-Driven Decisions**: Provide skill recommendations based on real market data
- **Real-Time Information**: Get the latest career information from authoritative sources like O*NET
- **Visual Analysis**: Intuitively display skill demand and trends through charts
- **Personalized Recommendations**: Provide customized skill suggestions based on target roles

### 👥 Target Audience

- Undergraduate and graduate students
- Recent graduates
- Career changers
- Job seekers
- Career planning consultants

### 🚀 Key Features

#### 1. Data Scraping
- **O*NET Data Scraping**: Extract career information from the U.S. Department of Labor's O*NET database
- **Multi-Source Data Integration**: Support for extending to other data sources (Indeed, Glassdoor, etc.)
- **Smart Retry Mechanism**: Automatically handle network errors and anti-scraping measures

#### 2. Skills Analysis
- **Skill Frequency Statistics**: Analyze the most popular technical skills
- **Skill Categorization**: Classify by programming languages, data analysis, cloud computing, etc.
- **Trend Analysis**: Identify changes in skill demand trends

#### 3. Visualization
- **Static Charts**: Create professional charts using matplotlib and seaborn
- **Interactive Charts**: Create interactive data visualizations using plotly
- **Multi-Dimensional Analysis**: Display skill data from different perspectives

#### 4. Search and Recommendations
- **Smart Search**: Search for related careers based on keywords
- **Skill Recommendations**: Provide personalized skill suggestions for target roles
- **Career Matching**: Help users find the most suitable career paths

### 📋 Tech Stack

- **Programming Language**: Python 3.8+
- **Web Scraping**: requests, BeautifulSoup4
- **Data Processing**: pandas, numpy
- **Data Visualization**: matplotlib, seaborn, plotly
- **Text Analysis**: NLTK, spaCy (optional)
- **API Integration**: BLS Labor Statistics API (planned)

### 🛠️ Installation Guide

#### 1. Requirements
- Python 3.8 or higher
- pip package manager

#### 2. Installation Steps

```bash
# 1. Clone or download the project
git clone <repository-url>
cd job-market-analyzer

# 2. Create virtual environment (recommended)
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the program
python job_market_analyzer.py
```

#### 3. Optional Configuration

```bash
# Install Chinese font support (if you encounter Chinese display issues)
pip install matplotlib-font-manager

# Install spaCy language model (for advanced text analysis)
python -m spacy download en_core_web_sm
```

### 📖 Usage Guide

#### Basic Usage Workflow

1. **Start the Program**
   ```bash
   python job_market_analyzer.py
   ```

2. **Select Operation**
   - Choose `1` to start scraping O*NET data
   - Enter the maximum number of occupations to scrape (recommended 50-100)

3. **Analyze Data**
   - Choose `2` for skills analysis
   - View the most popular skills statistics

4. **Search Function**
   - Choose `3` to search for specific skills or careers
   - Enter keywords to search

5. **Get Recommendations**
   - Choose `4` to get skill recommendations
   - Enter target role (e.g., data scientist)

6. **Visualization**
   - Choose `5` to create visualization charts
   - View static and interactive charts

7. **Save Data**
   - Choose `6` to save scraped data
   - Data will be saved in JSON format

#### Advanced Features

##### Batch Data Processing
```python
from job_market_analyzer import JobMarketAnalyzer

# Create analyzer instance
analyzer = JobMarketAnalyzer()

# Scrape large amounts of data
data = analyzer.scrape_onet_data(max_occupations=200)

# Analyze skills
skills_df = analyzer.analyze_skills()

# Get recommendations for specific roles
recommendations = analyzer.get_skill_recommendations("data scientist")
```

##### Custom Skill Keywords
```python
# Add custom skill keywords
analyzer.tech_skills.extend(['React Native', 'Flutter', 'Vue.js'])
```

### 📊 Data Sources

#### O*NET Database
- **Source**: U.S. Department of Labor's Occupational Information Network
- **Data Types**: Job descriptions, skill requirements, salary information, education requirements
- **Update Frequency**: Regular updates
- **Coverage**: U.S. job market

#### Planned Data Sources
- **BLS Labor Statistics**: Employment growth rates and salary statistics
- **Indeed API**: Real-time job postings
- **LinkedIn Data**: Skill trends and certification information

### 📈 Output Examples

#### Skills Analysis Results
```
Top 20 Most In-Demand Skills:
1. Python          - 45 occurrences (90.0%)
2. SQL             - 38 occurrences (76.0%)
3. JavaScript      - 32 occurrences (64.0%)
4. Java            - 28 occurrences (56.0%)
5. Machine Learning - 25 occurrences (50.0%)
...
```

#### Visualization Charts
- Skill frequency bar charts
- Skill distribution pie charts
- Skill trend line charts
- Interactive skill analysis dashboard

### 🔧 Configuration Options

#### Scraper Settings
```python
# Modify request headers
analyzer.headers.update({
    'User-Agent': 'Your-Custom-User-Agent'
})

# Set delay time
time.sleep(2)  # Increase delay to avoid being blocked
```

#### Custom Skill Keywords
```python
# Add new skill keywords
custom_skills = ['Docker', 'Kubernetes', 'Terraform']
analyzer.tech_skills.extend(custom_skills)
```

### 🚨 Important Notes

#### Legal and Ethical Considerations
- **Respect robots.txt**: Follow website scraping policies
- **Reasonable Use**: Avoid placing excessive load on target websites
- **Data Usage**: For learning and research purposes only

#### Technical Limitations
- **Anti-Scraping Measures**: Some websites may have anti-scraping protection
- **Data Updates**: Scraped data may not be the latest
- **Network Dependency**: Requires stable internet connection

#### Performance Optimization
- **Batch Processing**: Recommend batch processing for large amounts of data
- **Memory Management**: Regularly clean up unnecessary data
- **Caching Mechanism**: Can save data to avoid repeated scraping

### 🐛 Troubleshooting

#### Common Issues

1. **Scraping Failure**
   ```
   Solutions:
   - Check network connection
   - Increase retry count
   - Check if target website is accessible
   ```

2. **Chinese Display Issues**
   ```
   Solutions:
   - Install Chinese font packages
   - Set matplotlib fonts
   - Use UTF-8 encoding
   ```

3. **Dependency Conflicts**
   ```
   Solutions:
   - Use virtual environment
   - Update pip version
   - Check Python version compatibility
   ```

#### Debug Mode
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# View scraping details
analyzer = JobMarketAnalyzer()
soup = analyzer.get_page(url)
print(soup.prettify())
```

### 🔮 Future Plans

#### Short-term Goals (1-2 months)
- [ ] Integrate BLS Labor Statistics API
- [ ] Add Indeed job scraper
- [ ] Implement data caching mechanism
- [ ] Optimize scraper performance

#### Medium-term Goals (3-6 months)
- [ ] Develop web interface
- [ ] Add user account system
- [ ] Implement data export functionality
- [ ] Support multi-language interface

#### Long-term Goals (6-12 months)
- [ ] Machine learning skill prediction
- [ ] Real-time data updates
- [ ] Mobile application
- [ ] API service

### 🤝 Contributing

We welcome community contributions! Please follow these steps:

1. **Fork the Project**
2. **Create Feature Branch**: `git checkout -b feature/AmazingFeature`
3. **Commit Changes**: `git commit -m 'Add some AmazingFeature'`
4. **Push Branch**: `git push origin feature/AmazingFeature`
5. **Create Pull Request**

#### Contribution Types
- 🐛 Bug fixes
- ✨ New features
- 📚 Documentation improvements
- 🎨 Code optimization
- 🧪 Test cases

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 👨‍💻 Development Team

**Orange Team**
- Project Lead: [Your Name]
- Main Developers: [Developer Names]
- Data Scientists: [Data Scientist Names]

### 📞 Contact

- **Project Homepage**: [GitHub Repository URL]
- **Issue Reports**: [Issues Page]
- **Email**: [Contact Email]
- **Documentation**: [Documentation URL]

### 🙏 Acknowledgments

Thanks to the following open source projects and services:
- [O*NET](https://www.onetonline.org/) - Career data source
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [pandas](https://pandas.pydata.org/) - Data processing
- [matplotlib](https://matplotlib.org/) - Data visualization
- [plotly](https://plotly.com/) - Interactive charts

---

**⭐ If this project helps you, please give us a star!**