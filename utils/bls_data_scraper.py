"""
------------------------------------------------------------
File: bls_data_scraper.py
Team: Orange Team
Members: 
    - Jiatong Li (jiatong4)
    - Esha Pandya (epandya)
    - Fan Yang (fy4)
    - Sumreen Fathima (sumreenf)

Description:
    Code to make api requests to BLS endpoints, and scrape BLS webpage, 
    and scrape Pittsburgh specific pdf of employment outlook data

Imports:
    - Imports from: requests, json, pandas, matplotlib, beautifulsoup, pdfplumber, re
    - Imported by: app.py
------------------------------------------------------------
"""

import requests
import json
import pandas as pd 
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import pdfplumber
import re


#API Pulls for data related to employment stats, wage stats in tech industry
def fetch_bls_data(api_key):
    headers = {'Content-type': 'application/json'}
    series_id = {
     "CES0500000003": "Average hourly earnings of all employees, total private in the United States", 
     "LNS11000000": "Civilian Labor Force (Seasonally Adjusted)",
     "LNS14000000": "Civilian Unemployment Rate (Seasonally Adjusted)",
     "LNS12000000": "Civilian Employment Level (Seasonally Adjusted)",
     "LNS13000000": "Civilian Unemployment Level (Seasonally Adjusted)"
     }
    for series in series_id:
        print(f"Fetching data for series: {series} - {series_id[series]}")
         # Prepare the payload
        payload = json.dumps({
            "seriesid": [series], 
            "startyear": "2014",
            "endyear": "2024",
            "registrationKey": api_key
        })
         # Send the request
        response = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/", data=payload, headers=headers)
   
        data = response.json()
    
        if data['status'] == 'REQUEST_SUCCEEDED':
            series_data = data['Results']['series'][0]['data']
       
        else:
            print("Failed to retrieve data:", data.get('message', 'Unknown error'))

        #Parse JSON response
        records = [
            {
                'Year': item['year'],
                'Month': item['periodName'],
                'Value': float(item['value']),
                'Date': (
                    f"{item['year']}-{item['period'][1:]}"
                    if 'M' in item['period']
                    else item['period'][:3]
                )
            }
            for item in reversed(series_data)
        ]

        # Organize data into dataframe
        df = pd.DataFrame(records)
    
        # Save to CSV
        df.to_csv(f"data/raw_data/{series}.csv", index=False)

    return


#Web-scrapping for Employment projections for jobs in tech industry:
def web_scrape_bls_employment_projections():
    url = "https://data.bls.gov/projections/nationalMatrix?queryParams=510000&ioType=i&_csrf=projections"
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    # get a list of all table tags
    table_list = soup.find_all('table')

    table = table_list[0]
    rows = table.find_all('tr')

    headers = []
    rows = []
    for th in table.find_all('th'):
        headers.append(th.text.strip())

    for tr in table.find_all('tr'):
        cells = tr.find_all('td')
        if len(cells) > 0:
            row = [cell.text.strip() for cell in cells]
            rows.append(row)

    df = pd.DataFrame(rows, columns=headers)
    code_col = df.columns[1]
 
    filtered_df = df[df[code_col].astype(str).str.startswith('15')]

    filtered_df.to_csv("data/raw_data/employment_projections_tech.csv", index=False)
    return

#Scrapes the pdf for pittsburgh wage outlooks
def pittsburgh_computer_wage_outlook():
    """
    Extract tables from a PDF and filter for computer-related occupations in Pittsburgh
    """ 
    pdf_path = "pghmsa_ow.pdf"  

    # Pattern to match SOC codes starting with 15-
    soc_pattern = re.compile(r'^15-\d{4}')

    matching_rows = []

    #Cleans pdf into rows to detect soc code for computer occupations
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
          
            for table in tables:
                columns = table[1]
                big_row = table[2]
               
                rows = big_row[0].split('\n')
                for row in rows:
                  
                    if re.match(soc_pattern, row):
                        print("Matched SOC code row:", row)
                        matching_rows.append(row)

        final_df = pd.DataFrame(matching_rows, columns=columns)

        final_df.to_csv("data/raw_data/pittsburgh_computer_wage_outlook.csv", index=False)

    return
