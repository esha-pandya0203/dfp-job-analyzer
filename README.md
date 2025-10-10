# Orange Team - Job Analyzer Project

## Team Members
- **Jiatong Li** (`jiatong4`)
- **Esha Pandya** (`epandya`)
- **Fan Yang** (`fy4`)
- **Sumreen Fathima** (`sumreenf`)

## Create Virtual Environment 
# Windows 
```bash
python -m venv venv
venv\Scripts\Activate 
```
# MacOS 
```bash
python -m venv venv
source .venv/bin/activate
``` 

## Installation
```bash
pip install -r requirements.txt
```

## Run the App
```bash
streamlit run app.py
```

## On Startup: 
The user will see a prompt asking if they would like to use previously scraped data or download new data, which can take up to 15 minutes. 

## Dashboard: 
Displays trends of employment in the United States including employment/unemployment rates, percent of occupation, percent of industry, and top skills in the technical field. 

## Job Search: 
The user will be able to search a pre-selected list of job titles and view information such as its title, company, salary, skills, experience level, and application link. 
