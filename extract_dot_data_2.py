import pandas as pd
import re
# import requests
import urllib.request
import pdfplumber
from bs4 import BeautifulSoup
import os
import datetime

### DICTIONARIES ###
# Used to convert month to numerical value
months_dict = {'january': 1, 'february': 2, 'march': 3, 'april':4, 'may': 5, 
               'june': 6, 'july': 7, 'august': 8, 'september': 9, 'october': 10,
               'november': 11, 'december': 12, 'jan': 1, 'feb': 2, 'mar': 3, 'apr':4,
               'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}

# Used to convert month to numerical quarter value
quarters_dict = {'january': 1, 'april':2, 'july': 3, 'october': 4,
                 'jan': 1, 'apr':2, 'jul': 3, 'oct': 4}

# Used to define different metric features
features_dict = {'mishandled_baggage': ['Number of Bags Enplaned',
                                        'Number of Bags Mishandled',
                                        'Number of Bags Mishandled Per 1000 Enplaned'],
                 
                'mishandled_ws': ['Number of Wheelchairs and Scooters Enplaned',
                                  'Number of Wheelchairs and Scooters Mishandled',
                                  'Percent of wheelchairs and Scooters Mishandled'],
                 
                'denied_boarding': ['Voluntary', 
                                    'Involuntary', 
                                    'Enplaned', 
                                    'Involuntary DB Per 10000 Passengers']}

# used to reorder dataframe features
features_order = {'mishandled_baggage': ['Carrier', 
                                        'Year',
                                        'Month',
                                        'Number of Bags Enplaned',
                                        'Number of Bags Mishandled',
                                        'Number of Bags Mishandled Per 1000 Enplaned'],
                 
                'mishandled_ws': ['Carrier', 
                                  'Year',
                                  'Month',
                                  'Number of Wheelchairs and Scooters Enplaned',
                                  'Number of Wheelchairs and Scooters Mishandled',
                                  'Percent of wheelchairs and Scooters Mishandled'],
                 
                'denied_boarding': ['Carrier', 
                                    'Year',
                                    'Quarter',
                                    'Voluntary', 
                                    'Involuntary', 
                                    'Enplaned', 
                                    'Involuntary DB Per 10000 Passengers']}
    
### FUNCTIONS ###
# Contains the name of the reports that have been updated
def update_reports():
    """
    Updates which DOT reports have been added.
    """
    return os.listdir('./reports')

def update_csv():
    """
    Updates which csv have been added.
    """
    return os.listdir('./data')

def beautify_page(url="https://www.transportation.gov/individuals/aviation-consumer-protection/air-travel-consumer-reports-2020"):
    """
    returns BeautifulSoup object that can be used to parse.
    
    Args:
    url (str) : URL that contains links to DOT reports
    
    Returns:
    soup (obj) : BeautifulSoup object
    """
    # page = requests.get(url)
    page = urllib.request.urlopen(url)
    if page.getcode() == 200:
        soup = BeautifulSoup(page.read(), 'html.parser')
        print('Connection Successful!')
        print(url)
        return soup
    else:
        print('Connection Failure!')
        print(f'Status Code: {page.status_code}')

def get_all_pdf(soup):
    """
    Extracts all the pdf links from beautified soup of DOT website
    
    Args:
    soup (obj) : Beautiful Soup object 
    
    Returns:
    list_to_update (list) : list of pdf links to DOT data
    """
    
    list_to_update = []
    report = soup.find_all('div', class_='mb-4 clearfix')
    
    for a in report[0].find_all('a', href=True):
        sub_link = a['href']
        if 'individual' in sub_link:
            if not (sub_link.startswith('http') or sub_link.startswith('www')):
                sub_link = 'https://www.transportation.gov' + sub_link
            sub_page = beautify_page(sub_link)

            list_to_update.append(sub_page.find(class_='file').find('a')['href'])
            
    return list_to_update

# Source: https://www.youtube.com/watch?v=eTz3VZmNPSE
def download_pdf(url):
    """
    Saves pdf files to local directory
    
    Args:
    url (str) : string that contains PDF url information
    
    Returns:
    (str) : string that shows the local directory of where the pdf file is stored
    """
    # Extracts the last part of the URL to be used as the name of the file
    local_filename = url.split('/')[-1].replace('%','')
    
    if local_filename not in REPORTS:
        with urllib.request.urlopen(url) as r:
            with open(f'reports/{local_filename}', 'wb') as f:
                f.write(r.read())
                
        # updates report files in the directory
        return f'reports/{local_filename}'
    else:
        print(f'Already in the database - {local_filename}')
        return False

def find_operating_page_numbers(filename):
    """
    Finds page numbers for operating metrics.
    
    Args:
    filename (str) : Directory for DOT pdf file.
    
    Returns:
    operating_pages (list) : list of page numbers where the following are located [index]:
        [0]: Mishandled baggages
        [1]: Mishandled wheelchairs and scooters
        [2]: Denied Boarding
    """
    with pdfplumber.open(filename) as pdf:
        page = pdf.pages[1] # page 41 is missing baggage information
        text = page.extract_text()
    op_re_exp = r'(Operating Carrier (\(Monthly\)|\(Quarterly\)) \s*\d{1,})|(Reporting Carrier(\s*|\s\(Quarterly\)\s*)\d{1,})'
    re_operating_pages = re.compile(op_re_exp)
    
    operating_pages = [] # mishandled baggage / mishandled wheelchairs
    for line in text.split('\n'):
        if re_operating_pages.search(line):
            operating_pages.append(int(list(filter(lambda x: x!='', line.split(' ')))[-1]))
    if len(operating_pages) < 3:
        print('There are only 3 operating pages!')
    return operating_pages

### Mishandled baggages/wheelchairs/scooters Data Extraction ###
def get_table_values_monthly(filename, page_num):
    """
    Extracts monthly values out of pdf file.
    
    Args: 
    filename (str) : string that contains local directory of DOT pdf file
    
    page_num (int) : integer that shows the page number in PDF file with desired data
    
    Returns:
    carrier_names (list) : list of airline carriers in order appeared in pdf
    
    values (list) : list metric values extracted from pdf (same order as carrier_names)
    
    month (int) : month (M)
    
    year (int) : year (YYYY)
    """
    with pdfplumber.open(filename) as pdf:
        page = pdf.pages[page_num - 1] 
        text = page.extract_text()

    # Regex
    re_month = re.compile(r'^[A-Za-z]*.\d{2,}') # Finds the month/year
    re_new_rank = re.compile(r'^\d{1,}\s*[A-Z].*') # finds indices
    re_carrier_name = re.compile(r'[A-Z].*[A-Z]') # Carrier Name

    # instantiate lists for values
    values = []
    carrier_names = []
    month = None
    for i, line in enumerate(text.split('\n')):
        # Extracts month infomation
        if not month and re_month.search(line):
            if '-' in line:
                month = months_dict[line.split('-')[0].lower()]
                year = int('20'+line.split('-')[1][:2])
            else:
                month = months_dict[line.split(' ')[0].lower()]
                year = int(line.split(' ')[1])
        if re_new_rank.match(line):
            try:
                carrier_names.append(re_carrier_name.search(line)[0])

            except:
                print(f'An error has occured while parsing through a line. [Carrier Name] Line number {i}')
                print(line)
            try:
                # Filters out all empty strings from the list
                vals = list(filter(lambda x: x!='', line.split('  ')))[2:5]

                # Converts string to numerical values int or float
                vals = [int(x.replace(',', '')) if i!=len(vals)-1 else float(x) for i, x in enumerate(vals)]


                values.append(vals)
            except:
                print(f'An error has occured while parsing through a line. [MB or WS] Line number {i}')
                print(line)
    return carrier_names, values, month, year

### Denied Boarding Data Extraction ###
def get_table_values_quarterly(filename, page_num): 
    """
    Extracts quarterly values out of pdf file.
    
    Args: 
    filename (str) : string that contains local directory of DOT pdf file
    
    page_num (int) : integer that shows the page number in PDF file with desired data
    
    Returns:
    carrier_names (list) : list of airline carriers in order appeared in pdf
    
    values (list) : list metric values extracted from pdf (same order as carrier_names)
    
    quarter (int) : quarter (1-4)
    
    year (int) : year (YYYY)
    """
    with pdfplumber.open(filename) as pdf:
        page = pdf.pages[page_num - 1] 
        text = page.extract_text()

    # Regex
    re_month = re.compile(r'^[A-Za-z]*.-.[A-Za-z]*.\d{2,}') # Finds the month/year
    re_new_rank = re.compile(r'^\d{1,}\s*[A-Z].*') # finds indices
    re_carrier_name = re.compile(r'[A-Z].*[A-Z]') # Carrier Name

    # instantiate lists for values
    values = []
    carrier_names = []
    quarter = None
    for i, line in enumerate(text.split('\n')):
        # Extracts time infomation
        if not quarter and re_month.search(line):
            quarter = quarters_dict[line.split(' ')[0].split('-')[0].lower()]
#             year = int(line.split(' ')[2])
            year = re.search('\d{2,}', line)[0]
    
            if len(year) == 2:
                year = int('20' + year) # adds 2000 to the year
            else:
                year = int(year)
                
        if re_new_rank.match(line):
            try:
                carrier_names.append(re_carrier_name.search(line)[0])

            except:
                print(f'An error has occured while parsing through a line. [Carrier Name] Line number {i}')
                print(line)
            try:
                # Filters out all empty strings from the list
                vals = list(filter(lambda x: x!='', line.split('  ')))[2:6]

                vals = [int(x.replace(',', '')) if i!=len(vals)-1 else float(x) for i, x in enumerate(vals)]

                values.append(vals)
            except:
                print(f'An error has occured while parsing through a line. [Denied Boarding] Line number {i}')
                print(line)
    return carrier_names, values, quarter, year


if __name__ == "__main__":
    # DOT websites that contains reports
    REPORTS = update_reports()

    # this will run through 2020 and 2021 websites
    urls = ['https://www.transportation.gov/individuals/aviation-consumer-protection/air-travel-consumer-reports-2020', 
            'https://www.transportation.gov/individuals/aviation-consumer-protection/air-travel-consumer-reports-2021']
    
    for url in urls:
        # Instantiate dataframes
        df_mb = pd.DataFrame() # missing baggages
        df_ws = pd.DataFrame() # missing wheelchair/scooters
        df_db = pd.DataFrame() # denied boarding

        # Gets the DOT page with reports
        soup = beautify_page(url)

        # Gets list of URL that are available on DOT site
        list_to_update = get_all_pdf(soup)

        for i, url in enumerate(list_to_update[::-1]):
            filename = download_pdf(url)
            print(f'({i+1}/{len(list_to_update)}) {filename}')
            if filename:
                operating_pages = find_operating_page_numbers(filename)
                print(operating_pages)
                
                ## Mishandling Baggages ##
                print('Processing... Mishandling Baggages')
                carrier_names, values, month, year = get_table_values_monthly(filename, operating_pages[0])
                # Creating DataFrame

                df = pd.DataFrame(values)
                df.columns = features_dict['mishandled_baggage']
                df['Carrier'] = carrier_names
                df['Month'] = month
                df['Year'] = year
                
                df_mb = pd.concat([df_mb, df], axis=0)
                # Changes the order of the features
                df_mb = df_mb[features_order['mishandled_baggage']]
                m = '0'+str(month) if len(str(month))==1 else str(month)
                file_name_mb = f'MB_{m}_{year}.csv'
                
                ## Mishandling Wheelchairs and Scooters ##
                print('Processing... Mishandling W/S')
                carrier_names, values, month, year = get_table_values_monthly(filename, operating_pages[1])
                # Creating DataFrame

                df = pd.DataFrame(values)
                df.columns = features_dict['mishandled_ws']
                df['Carrier'] = carrier_names
                df['Month'] = month
                df['Year'] = year
                
                df_ws = pd.concat([df_ws, df], axis=0)
                # Changes the order of the features
                df_ws = df_ws[features_order['mishandled_ws']]
                m = '0'+str(month) if len(str(month))==1 else str(month)
                file_name_ws = f'WS_{m}_{year}.csv'

                ## Denied Boarding ##
                print('Processing... Denied Boarding')
                carrier_names, values, quarter, year = get_table_values_quarterly(filename, operating_pages[2])
                # Creating DataFrame

                df = pd.DataFrame(values)
                df.columns = features_dict['denied_boarding']
                df['Carrier'] = carrier_names
                df['Quarter'] = quarter
                df['Year'] = year
                
                df_db = pd.concat([df_db, df], axis=0)
                # Changes the order of the features
                df_db = df_db[features_order['denied_boarding']]
                file_name_db = f'DB_Q{quarter}_{year}.csv'

                REPORTS = update_reports()

                df_mb.to_csv(f'data/{file_name_mb}', index = False)
                df_ws.to_csv(f'data/{file_name_ws}', index = False)
                df_db.to_csv(f'data/{file_name_db}', index = False)
                print(f'CSV Files have been saved.')

    print(f'All {len(list_to_update)} files processed!')
