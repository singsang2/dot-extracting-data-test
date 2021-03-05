# dot-extracting-data-test
# Composition
**Directories:**
- <a href='./data'>`/data`</a> : this folder contains `csv` files of data extracted from reports in `/reports` directory
- <a href='./reports'>`/reports`</a> : this folder contains Air Travel Consumer Reports for 2020 and 2021 downloaded from DOT websites

**Files:**
- <a href='DOT_Extraction_Exploration.ipynb'>`DOT_Extraction_Exploration.ipynb`</a>: Jupyter notebook file where data extraction was explored
- <a href='extract_dot_data.py'>`extract_dot_data.py`</a> : main python file that can be run to extract data from DOT about Air Travel Consumer Reports
- <a href='extract_dot_data_2.py'>`extract_dot_data_2.py`</a> : main python file that can be run to extract data from DOT about Air Travel Consumer Reports (saves seperate csv files)

# Purpose
The main purposes of this project are
    
[1] Extract `mishandled baggages` data

[2] Extract `mishandled wheelchairs and scooters` data

[3] Extract `denied boarding` data
for different airlines in different months/years/quarters.

# Limitation
- The current program only works for reports since 2020. *Other reports have not been tested.
- The extracted data are converted to CSV file but it can be altered depending on needs.
- The current program only extracts the following data:
        
        [1] mishandled baggages

        [2] mishandled wheelchairs and scooters

        [3] denied boarding
- When running <a href='extract_dot_data.py'>`extract_dot_data.py`</a>, `denied boarding` information get duplicated because DOT posts same quarterly data multiple times. This can be fixed easily by deleting duplicated rows.

# Test Instruction
If you would like to test out the code follow the instruction:
- delete all the PDF reports from <a href='./reports'>`/reports`</a> directory.
- Run <a href='extract_dot_data.py'>`extract_dot_data.py`</a> or <a href='extract_dot_data_2.py'>`extract_dot_data_2.py`</a>
- Wait and see!

