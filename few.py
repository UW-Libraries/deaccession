#!/usr/bin/env python3
# coding: utf8

'''This script is used to find items held by a limited number of
Orbis Cascade Alliance members.
'''

import sys
import argparse
import json
from lxml import etree as ET
import logging
from urllib.parse import urljoin
import requests

LOGGER = logging.getLogger(__name__)

ALLIANCE_SYMBOLS = set([
    'CCD', 'CCV', 'CEO', 'CHK', 'CWU', 'EI1', 'EI1SP', 'EOS', 'ESR', 'GFC',
    'HTM', 'MHD', 'MRY', 'NTD', 'NTE', 'NTESP', 'OHS', 'OIT', 'OLC', 'OLE',
    'OLL', 'OLP', 'ONA', 'ONS', 'OPU', 'OQH', 'OQP', 'OR1', 'ORC', 'ORE',
    'ORU', 'ORUSP', 'ORZ', 'OUP', 'OWP', 'OWS', 'OWT', 'OXF', 'OXG', 'SOS',
    'UOL', 'UPP', 'W9L', 'WAU', 'WE2', 'WEA', 'WEV', 'WOS', 'WS2', 'WS2SP',
    'WS7', 'WS7SP', 'WSE', 'WSL', 'XFF', 'XOE', 'ZXQ'
])

# --- Prep data

def extract_holders(response, alliance_only=False):
    root = ET.fromstring(bytes(response, 'utf-8'))
    holdings = root.findall('holding')
    holders = set(h.find('institutionIdentifier/value').text for h in holdings)
    if alliance_only:
        holders &= ALLIANCE_SYMBOLS
    return holders


def filter_few(limit, recs):
    return [rec for rec in recs if len(rec['holders']) <= limit]

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

# --- I/O etc.

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


def get_api_data(api_key, oclc_number):
    '''Get WorldCat search info for a given OCLC number'''
    base = 'http://www.worldcat.org/webservices/catalog/content/libraries'
    rest = '{}?wskey={}&location=98195&maximumLibraries=100&libtype=1'
    url_template = urljoin(base, rest)
    url = url_template.format(oclc_number, api_key)
    LOGGER.debug('WorldCat request: {}'.format(url))
    response = requests.get(url)
    if response.status_code != 200:
        response.raise_for_status()
    LOGGER.debug('WorldCat response headers: {}'.format(response.headers))
    LOGGER.debug('WorldCat data: {}'.format(response.text))
    return response.text


def main():
    args = get_args()
    alliance_only = not args['worldcat']
    log_level = logging.DEBUG if args['debug'] else logging.ERROR
    logging.basicConfig(level=log_level)
    LOGGER.debug('runtime arguments = {}'.format(args))
    api_responses = (
        (oclc_number, get_api_data(args['wc_api_key'], oclc_number))
        for oclc_number in oclc_numbers(args['datafile'])
    )
    recs = [
        {'oclcnum': oclc_number, 'holders': extract_holders(response, alliance_only)}
        for (oclc_number, response) in api_responses
    ]
    LOGGER.debug('Data: {}'.format(recs))
    filtered = filter_few(args['limit'], recs)
    LOGGER.debug('Filtered data: {}'.format(filtered))
    assert all(args['home_institution_symbol'] in rec['holders'] for rec in filtered)
    print(render_recs(args['worldcat'], args['limit'], args['verbose'], filtered))


if __name__ == "__main__":
    sys.exit(main())

