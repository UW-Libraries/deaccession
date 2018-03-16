import unittest
import json
import few

class TestGetAllianceHolders(unittest.TestCase):
    def test_none(self):
        wc_search_result = {'library': []}
        result = few.get_alliance_holders(wc_search_result)
        self.assertFalse(result)

    def test_single(self):
        wc_search_result = {'library': [{'oclcSymbol': 'CCD'}]}
        result = few.get_alliance_holders(wc_search_result)
        expected = set(['CCD'])
        self.assertEqual(result, expected)

    def test_two_in_one_not_in(self):
        wc_search_result = {
            'library': [
                {'oclcSymbol': 'WAU'},
                {'oclcSymbol': 'CCD'},
                {'oclcSymbol': 'XXX'},
            ]
        }
        result = few.get_alliance_holders(wc_search_result)
        expected = set(['CCD', 'WAU'])
        self.assertEqual(result, expected)
if __name__ == '__main__':
    unittest.main()
