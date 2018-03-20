import requests
import os
import sys
import argparse
import json


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

def get_config(configfile):
    '''Load configuration file settings'''
    with open(configfile) as fh:
        config = json.load(fh)
    return config

def set_defaults(args):
    '''Set defaults for arguments that are not specified'''
    if not args['config']:
        args['config'] = 'config.json'
    if not args['limit']:
        args['limit'] = 1
    return args

def main(argv=None):
    parser = argparse.ArgumentParser(description='Show items that have limited holdings in Alliance libraries.')
    parser.add_argument("datafile", help="File with OCLC numbers to check")
    parser.add_argument("-c", "--config", help="Config file path (defaults to './config.json')")
    parser.add_argument("-l", "--limit", help="Holdings threshold (defaults to 1)", type=int)
    parser.add_argument('-v', '--verbose', action='store_true', help="Show detailed output")
    args = set_defaults(vars(parser.parse_args()))
    args.update(get_config(args['config']))

    datafile = args['datafile']
    api_key = args['wc_api_key']
    limit = args['limit']
    verbose = args['verbose']
    home_inst_symbol = args['home_institution_symbol']

    if verbose:
        print 'Home institution is %s' % home_inst_symbol
        print 'Show items with Alliance holdings <= %d' % limit
        print
    with open(datafile) as fh:
        for rawline in fh:
            oclc_number = rawline.strip()
            wc_data = get_wc_data(api_key, oclc_number)
            alliance_holders = get_alliance_holders(wc_data)
            assert(home_inst_symbol in alliance_holders)
            if len(alliance_holders) <= limit:
                if verbose:
                    print oclc_number, '|'.join(sorted(alliance_holders))
                else:
                    print oclc_number

if __name__ == "__main__":
    sys.exit(main())


# To-do
# confirm alliance symbol list is correct
# add logging
# add tests
# write up README
