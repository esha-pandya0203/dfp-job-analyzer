import requests
import json
import pandas as pd 
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

"""
API Pulls for data related to employment stats, wage stats in tech industry (information industry)
"""

l = {"CES5000000001": 'Information Industry, total nonfarm, number of employees in thousands', 
     "OEUN000000051--5215121003": "Hourly mean wage for Computer and Information Analysts in Sector 51 - Information in the United States", 
     "OEUN000000051--5215121004": "Annual mean wage for Computer and Information Analysts in Sector 51 - Information in the United States"
     }

# Replace this with your actual API key
API_KEY = "fb82158c02e24ee0ac0f39a32ccf3dc2"

# Set the headers and payload
headers = {'Content-type': 'application/json'}
payload = json.dumps({
    "seriesid": ["CES0500000003"], 
    "startyear": "2015",
    "endyear": "2024",
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
        'Date': f"{item['year']}-{item['period'][1:]}"
    }
    for item in reversed(series_data) 
    if 'M' in item['period']
]

print("records", records)

df = pd.DataFrame(records)
print(df)
#df.to_csv("Avg_Hourly_Earning_of_All_Employees.csv", index=False)

"""
Web-scrapping for Employment projections for jobs in tech industry:
"""

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
filtered_df.to_csv('employment_projections_tech.csv', index=False)
