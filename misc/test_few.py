#!/usr/bin/env python3
# coding: utf8

import unittest
import json
import few


class TestExtractHolders(unittest.TestCase):
    API_DATA = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<holdings xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.loc.gov/standards/iso20775/N121_ISOholdings_v4.xsd">
<holding>
<institutionIdentifier>
<value>WAU</value>
</institutionIdentifier>
</holding>
<holding>
<institutionIdentifier>
<value>CCD</value>
</institutionIdentifier>
</holding>
<holding>
<institutionIdentifier>
<value>XXX</value>
</institutionIdentifier>
</holding>
</holdings>"""

    def test_unrestricted_response(self):
        oclc_number = '12345'
        expected = set(['WAU', 'CCD', 'XXX'])
        response = few.extract_holders(TestExtractHolders.API_DATA)
        self.assertEqual(response, expected)

    def test_alliance_only_response(self):
        oclc_number = '12345'
        expected = set(['WAU', 'CCD'])
        response = few.extract_holders(TestExtractHolders.API_DATA, True)
        self.assertEqual(response, expected)


class TestFilterFew(unittest.TestCase):
    def test_more_than_limit(self):
        recs = [{
            'oclcnum': '12345',
            'holders': set(['WAU', 'CCD', 'XXX'])
        }]
        result = few.filter_few(2, recs)
        self.assertEqual(result, [])

    def test_equal_to_limit(self):
        recs = [{
            'oclcnum': '12345',
            'holders': set(['WAU', 'CCD'])
        }]
        expected = [{
            'oclcnum': '12345',
            'holders': set(['WAU', 'CCD'])
        }]
        result = few.filter_few(2, recs)
        self.assertEqual(result, expected)

    def test_fewer_than_limit(self):
        recs = [{
            'oclcnum': '12345',
            'holders': set(['WAU'])
        }]
        expected = [{
            'oclcnum': '12345',
            'holders': set(['WAU'])
        }]
        result = few.filter_few(2, recs)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
