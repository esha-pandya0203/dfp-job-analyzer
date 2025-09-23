import requests
import json
import pandas as pd 
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

"""
API Pulls for data related to employment stats, wage stats in tech industry (information industry)
"""

target_data = {"CES5000000001": 'Information Industry, total nonfarm, number of employees in thousands', 
     "OEUN000000051--5215121003": "Hourly mean wage for Computer and Information Analysts in Sector 51 - Information in the United States", 
     "OEUN000000051--5215121004": "Annual mean wage for Computer and Information Analysts in Sector 51 - Information in the United States", 
     "CES0500000003": "Average hourly earnings of all employees, total private in the United States", 
     "LNS11000000": "Civilian Labor Force (Seasonally Adjusted)",
     "LNS14000000": "Civilian Unemployment Rate (Seasonally Adjusted)",
     "LNS12000000": "Civilian Employment Level (Seasonally Adjusted)",
     "LNS13000000": "Civilian Unemployment Level (Seasonally Adjusted)"
     }

# Replace this with your actual API key
API_KEY = "fb82158c02e24ee0ac0f39a32ccf3dc2"


def fetch_bls_data(series_id, start_year, end_year):
    headers = {'Content-type': 'application/json'}
    for series in series_id:
        print(f"Fetching data for series: {series} - {series_id[series]}")
         # Prepare the payload
        payload = json.dumps({
            "seriesid": [series], 
            "startyear": start_year,
            "endyear": end_year,
            "registrationKey": API_KEY
        })
         # Send the request
        response = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/", data=payload, headers=headers)
        print(response)
        data = response.json()
        print(json.dumps(data, indent=2))

        if data['status'] == 'REQUEST_SUCCEEDED':
            series_data = data['Results']['series'][0]['data']
            print(series_data)
        else:
            print("Failed to retrieve data:", data.get('message', 'Unknown error'))
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

        print("records", records)

        df = pd.DataFrame(records)
        print(df)
        #df.to_csv(f"{series_id[0]}.csv", index=False)

    return


"""
Web-scrapping for Employment projections for jobs in tech industry:
"""

def web_scrape_bls_employment_projectsions():
    url = "https://data.bls.gov/projections/nationalMatrix?queryParams=510000&ioType=i&_csrf=projections"
    response = requests.get(url)
    print(response)
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup.prettify())

    # get a list of all table tags
    table_list = soup.find_all('table')

    # how many are there?
    print('there is/are', len(table_list), 'table/s')
    table = table_list[0]
    rows = table.find_all('tr')
    # how many rows are there?
    print('there are', len(rows), 'table rows')

    # first row (sub-0 row) contains column headers
    headers = rows[0].find_all('th')

    # how many columns are there?
    print('there are', len(headers), 'columns')
    for h in headers:
        print(h.contents)

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
    print(code_col)
    filtered_df = df[df[code_col].astype(str).str.startswith('15')]
    print(filtered_df)
    #filtered_df.to_csv('employment_projections_tech.csv', index=False)
    return


#fetch_bls_data(target_data, "2014", "2024")
web_scrape_bls_employment_projectsions()