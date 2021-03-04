# dot-extracting-data-test
# Composition
**Directories:**
- <a href='./data'>`/data`</a> : this folder contains `csv` files of data extracted from reports in `/reports` directory
- <a href='./reports'>`/reports`</a> : this folder contains Air Travel Consumer Reports for 2020 and 2021 downloaded from DOT websites

**Files:**
- `DOT_Extraction_Exploration.ipynb`: Jupyter notebook file where data extraction was explored
- `extract_dot_data.py` : main python file that can be run to extract data from DOT about Air Travel Consumer Reports

# Purpose
The main purposes of this project are
    
[1] Extract `mishandled baggage` data

[2] Extract `mishandled wheelchairs and scooters` data

[3] Extract `denied boarding` data
for different airlines in different months/years/quarters.

# Limitation
- The current program only works for reports since 2020. *Other reports have not been tested.
- The extracted data are converted to CSV file but it can be altered depending on needs.

# Test Instruction
If you would like to test out the code follow the instruction:
- delete all the PDF reports from <a href='./reports'>`/reports`</a> directory.
- Run `extract_dot_data.py`
- Wait and see!

