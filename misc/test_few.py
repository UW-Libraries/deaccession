import unittest
import json
import few


class TestSimplify(unittest.TestCase):
    def test_record_is_simplified(self):
        rec = {'OCLCnumber': 123, 'library': []}
        result = few.simplify_rec(True, rec)
        expected = {'oclcnum': 123, 'holders': set()}
        self.assertEqual(result, expected)


class TestFewHoldingsExist(unittest.TestCase):
    def test_more_holdings_than_limit(self):
        rec = {'oclcnum': 123, 'holders': set(['AAA', 'BBB'])}
        self.assertFalse(few.few_holdings_exist(1, rec))

    def test_holdings_equals_limit(self):
        rec = {'oclcnum': 123, 'holders': set(['AAA', 'BBB'])}
        self.assertTrue(few.few_holdings_exist(2, rec))

    def test_less_holdings_than_limit(self):
        rec = {'oclcnum': 123, 'holders': set(['AAA', 'BBB'])}
        self.assertTrue(few.few_holdings_exist(3, rec))


class TestFilterHoldings(unittest.TestCase):
    def test_filter_off(self):
        rec = {'oclcnum': 123, 'holders': set(['CCD', 'XXX'])}
        result = few.filter_holdings(True, rec)
        expected = {'oclcnum': 123, 'holders': set(['CCD', 'XXX'])}
        self.assertEqual(result, expected)

    def test_filter_on(self):
        rec = {'oclcnum': 123, 'holders': set(['CCD', 'XXX'])}
        result = few.filter_holdings(False, rec)
        expected = {'oclcnum': 123, 'holders': set(['CCD'])}
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
