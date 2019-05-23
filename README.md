# Deaccession/Weeding Utilities
Scripts for use in helping with deaccession/weeding library collections. Currently the only script is 'few.py'. This script takes a file containing OCLC numbers and finds ones that are held by N or fewer Orbis Cascade Alliance libraries (where N is specified by the user).  

## Getting Started

### Prerequisites

You will need Python 3.x and the lxml & requests library (install by running: `python3 -m pip install lxml requests`).  

### Installing

1. Clone the respository

    git clone https://github.com/UW-Libraries/deaccession.git  
    cd deaccession  

2. Create a config.json file.

    Copy the config.json.template file to config.json. Edit config.json adding a value for wc_api_key. The home_institution_symbol value is set to University of Washington (WAU). It can be changed to another institutions OCLC holdings symbol if desired.   

3. Run the script

    Enter ```python3 few.py -h``` at the command line. Usage instructions will appear.  

### Example usage

```python3 few.py --limit 3 <file-with-oclc-numbers>```   

This example will display all of the OCLC numbers from the given file that are held by 3 or fewer Orbis Cascade Alliance members. The file with OCLC numbers should contain one number per line. An example data file (example-data.txt) is in the *misc* folder  

```python3 few.py --limit 3 --verbose <file-with-oclc-numbers>```   

This example will do the same as above but will show additional information such as the holding symbol for each institution that has the item.  

Note: it is assumed that all of the OCLC numbers are held by the home institution set in config.json. If this is not the case for any of the numbers in the file, the script will exit with an error.  

