#!/usr/bin/env python2

'''This script is used to find items held by a limited number of
Orbis Cascade Alliance members.
'''

import sys
import argparse
import json
import logging
import urlparse
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

def get_alliance_holders(wc_search_result):
    '''Return all Alliance holder symbols for a WorldCat JSON search result'''
    all_holders = set([item['oclcSymbol'] for item in wc_search_result['library']])
    alliance_holders = all_holders & ALLIANCE_SYMBOLS
    return alliance_holders

def get_worldcat_holders(wc_search_result):
    '''Return all Alliance holder symbols for a WorldCat JSON search result'''
    return set([item['oclcSymbol'] for item in wc_search_result['library']])

def get_wc_data(api_key, oclc_number):
    '''Get WorldCat search info for a given OCLC number'''
    base = 'http://www.worldcat.org/webservices/catalog/content/libraries'
    rest = '%s?wskey=%s&format=json&location=98195&maximumLibraries=100&libtype=1'
    url_template = urlparse.urljoin(base, rest)
    url = url_template % (oclc_number, api_key)
    response = requests.get(url)
    if response.status_code != 200:
        response.raise_for_status()
    return response.json()

def get_config(configfilepath):
    '''Load configuration file settings'''
    with open(configfilepath) as configfile:
        config = json.load(configfile)
    return config

def set_defaults(args):
    '''Set defaults for arguments that are not specified'''
    if not args['config']:
        args['config'] = 'config.json'
    if not args['limit']:
        args['limit'] = 1
    return args

def output_record(args, oclc_number, holders):
    output = ''
    assert args['home_institution_symbol'] in holders
    if len(holders) <= args['limit']:
        if args['verbose']:
            holder_syms = '|'.join(sorted(holders))
            output += '%s\t%s' % (oclc_number, holder_syms)
        else:
            output += oclc_number
    return output

def output_worldcat(make_record, wc_data):
    holders = get_worldcat_holders(wc_data)
    return make_record(holders)

def output_alliance(make_record, wc_data):
    holders = get_alliance_holders(wc_data)
    return make_record(holders)

def make_outputter(wc):
    if wc:
        return output_worldcat
    else:
        return output_alliance

def make_header(wc, limit):
    if wc:
        scope = 'WorldCat'
    else:
        scope = 'Alliance'
    return 'Show items with %s holdings <= %d' % (scope, limit)

def main():
    parser_desc = 'Show items that have limited holdings in Alliance libraries.'
    parser = argparse.ArgumentParser(description=parser_desc)
    parser.add_argument("datafile", help="File with OCLC numbers to check")
    parser.add_argument("-c", "--config", help="Config file path (defaults to './config.json')")
    parser.add_argument("-l", "--limit", help="Holdings threshold (defaults to 1)", type=int)
    parser.add_argument('-v', '--verbose', action='store_true', help="Show detailed output")
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug logging")
    parser.add_argument("-w", "--worldcat", action='store_true', help="Search all WorldCat holdings (not just Alliance holdings)")
    args = set_defaults(vars(parser.parse_args()))
    args.update(get_config(args['config']))

    log_level = logging.DEBUG if args['debug'] else logging.ERROR
    logging.basicConfig(level=log_level)
    LOGGER.info('runtime arguments = %s', args)

    if args['verbose']:
        print make_header(args['worldcat'], args['limit'])
        print
    output_records = make_outputter(args['worldcat'])
    with open(args['datafile']) as datafile:
        for rawline in datafile:
            oclc_number = rawline.strip()
            wc_data = get_wc_data(args['wc_api_key'], oclc_number)
            LOGGER.debug('WorldCat data: %s', wc_data)
            make_record = partial(output_record, args, oclc_number)
            print output_records(make_record, wc_data)

if __name__ == "__main__":
    sys.exit(main())
