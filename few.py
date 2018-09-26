#!/usr/bin/env python3

'''This script is used to find items held by a limited number of
Orbis Cascade Alliance members.
'''

import sys
import argparse
import json
import logging
from urllib.parse import urljoin
import requests
from functools import partial

LOGGER = logging.getLogger(__name__)

ALLIANCE_SYMBOLS = set([
    'CCD', 'CCV', 'CEO', 'CHK', 'CWU', 'EI1', 'EI1SP', 'EOS', 'ESR', 'GFC',
    'HTM', 'MHD', 'MRY', 'NTD', 'NTE', 'NTESP', 'OHS', 'OIT', 'OLC', 'OLE',
    'OLL', 'OLP', 'ONA', 'ONS', 'OPU', 'OQH', 'OQP', 'OR1', 'ORC', 'ORE',
    'ORU', 'ORUSP', 'ORZ', 'OUP', 'OWP', 'OWS', 'OWT', 'OXF', 'OXG', 'SOS',
    'UOL', 'UPP', 'W9L', 'WAU', 'WE2', 'WEA', 'WEV', 'WOS', 'WS2', 'WS2SP',
    'WS7', 'WS7SP', 'WSE', 'WSL', 'XFF', 'XOE', 'ZXQ'
])

# --- Process API data for output

def process_recs(limit, wc, recs):
    '''Massage data for output by...
    1. Simplifying records to contain only relevant fields
    2. Selecting either all WorldCat holdings or just Alliance holdings
    3. Selecting only records that have few holdings
    '''
    simplify_recs = partial(map, partial(simplify_rec, wc))
    cull_holdings = partial(map, partial(filter_holdings, wc))
    filter_recs = partial(filter, partial(few_holdings_exist, limit))
    return list(filter_recs(cull_holdings(simplify_recs(recs))))

def simplify_rec(wc, rec):
    '''Eliminate irrelevant fields from record'''
    holders = set([item['oclcSymbol'] for item in rec['library']])
    return {
        'oclcnum': rec['OCLCnumber'],
        'holders': holders,
    }

def few_holdings_exist(limit, rec):
    '''Return True if number of holdings is <= limit'''
    return len(rec['holders']) <= limit

def filter_holdings(wc, rec):
    '''Eliminate non-Alliance holdings if requested'''
    if not wc:
        rec['holders'] &= ALLIANCE_SYMBOLS
    return rec

# --- Render ouput

def render_recs(wc, limit, verbose, recs):
    '''Create a string for output from input records'''
    lines = []
    if verbose:
        lines.append(render_header(wc, limit))
        lines.append('')
    for rec in recs:
        lines.append(render_rec(verbose, rec))
    return '\n'.join(lines)

def render_header(wc, limit):
    '''Create header string depending on holdings type requested'''
    scope = 'WorldCat' if wc else 'Alliance'
    return 'Show items with {} holdings <= {}'.format(scope, limit) 

def render_rec(verbose, rec):
    '''Create an output string for the record'''
    output = ''
    if verbose:
        holder_syms = '|'.join(sorted(rec['holders']))
        output += '{}\t{}'.format(rec['oclcnum'], holder_syms)
    else:
        output += rec['oclcnum']
    return output

# -----------------------------

def get_args():
    '''Get command line arguments as well as configuration settings'''
    parser_desc = 'Show items that have limited holdings in Alliance libraries.'
    parser = argparse.ArgumentParser(description=parser_desc)
    parser.add_argument("datafile", help="File with OCLC numbers to check")
    parser.add_argument("-c", "--config", help="Config file path (defaults to './config.json')", default='config.json')
    parser.add_argument("-l", "--limit", help="Holdings threshold (defaults to 1)", default=1, type=int)
    parser.add_argument('-v', '--verbose', action='store_true', help="Show detailed output")
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug logging")
    parser.add_argument("-w", "--worldcat", action='store_true', help="Search all WorldCat holdings (not just Alliance holdings)")
    args = vars(parser.parse_args())
    args.update(get_config(args['config']))
    return args

def get_api_data(api_key, oclc_number):
    '''Get WorldCat search info for a given OCLC number'''
    base = 'http://www.worldcat.org/webservices/catalog/content/libraries'
    rest = '{}?wskey={}&format=json&location=98195&maximumLibraries=100&libtype=1'
    url_template = urljoin(base, rest)
    url = url_template.format(oclc_number, api_key)
    response = requests.get(url)
    if response.status_code != 200:
        response.raise_for_status()
    data = response.json()
    LOGGER.debug('WorldCat data: {}'.format(data))
    return data

def get_config(configfilepath):
    '''Load configuration file settings'''
    with open(configfilepath) as configfile:
        config = json.load(configfile)
    return config

def oclc_numbers(datafile):
    '''Generator for OCLC number data'''
    with open(datafile) as data:
        for rawline in data:
            yield rawline.strip()

def get_records(get_data, oclc_nums):
    '''Generator for WorldCat data'''
    for oclc_number in oclc_nums:
        yield get_data(oclc_number)

def main():
    args = get_args()
    log_level = logging.DEBUG if args['debug'] else logging.ERROR
    logging.basicConfig(level=log_level)
    LOGGER.info('runtime arguments = {}'.format(args))

    get_data = partial(get_api_data, args['wc_api_key'])
    rawrecs = get_records(get_data, oclc_numbers(args['datafile']))
    recs = process_recs(args['limit'], args['worldcat'], rawrecs)
    # ensure that home institution exists in holdings
    assert all(args['home_institution_symbol'] in rec['holders'] for rec in recs)
    print(render_recs(args['worldcat'], args['limit'], args['verbose'], recs))

if __name__ == "__main__":
    sys.exit(main())
