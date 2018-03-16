import requests
import os
import sys

ALLIANCE_SYMBOLS = set([
    'CCD', 'CCV', 'CEO', 'CHK', 'CWU', 'EI1', 'EI1SP', 'EOS', 'ESR', 'GFC',
    'HTM', 'MHD', 'MRY', 'NTD', 'NTE', 'NTESP', 'OHS', 'OIT', 'OLC', 'OLE', 
    'OLL', 'OLP', 'ONA', 'ONS', 'OPU', 'OQH', 'OQP', 'OR1', 'ORC', 'ORE',
    'ORU', 'ORUSP', 'ORZ', 'OUP', 'OWP', 'OWS', 'OWT', 'OXF', 'OXG', 'SOS',
    'UOL', 'UPP', 'W9L', 'WAU', 'WE2', 'WEA', 'WEV', 'WOS', 'WS2', 'WS2SP',
    'WS7', 'WS7SP', 'WSE', 'WSL', 'XFF', 'XOE', 'ZXQ'
])

def get_alliance_holders(wc_search_result):
    '''Return all Alliance holder symbols for a WorldCat JSON search result'''
    all_holders = set([item['oclcSymbol'] for item in wc_search_result['library']])
    alliance_holders = all_holders & ALLIANCE_SYMBOLS
    return alliance_holders

def get_wc_data(api_key, oclc_number):
    '''Get WorldCat search info for a given OCLC number'''
    url_template = 'http://www.worldcat.org/webservices/catalog/content/libraries/%s?wskey=%s&format=json&location=98195&maximumLibraries=100&libtype=1'
    url = url_template % (oclc_number, api_key)
    r = requests.get(url)
    return r.json()

def get_api_key():
    '''Get WorldCat API key, assumed to be in same directory as this script
    and named "apikey.txt"'''
    execpath = os.path.dirname(os.path.realpath(__file__))
    keyfile = os.path.join(execpath, 'apikey.txt')
    with open(keyfile) as fh:
        return fh.read().strip()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    oclc_num_file = argv[1]
    home_inst_symbol = argv[2]
    limit = int(argv[3])
    api_key = get_api_key()
    with open(oclc_num_file) as fh:
        for rawline in fh:
            oclc_number = rawline.strip()
            wc_data = get_wc_data(api_key, oclc_number)
            alliance_holders = get_alliance_holders(wc_data)
            assert(home_inst_symbol in alliance_holders)
            if len(alliance_holders) <= limit:
                print oclc_number

if __name__ == "__main__":
    sys.exit(main())

# To-do
# add usage info to main()
# confirm alliance symbol list is correct
# add logging
# add tests
# make limit arg optional (default to limit=1)
