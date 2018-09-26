import unittest
from bamboohr_to_database import *


class TestRequests(unittest.TestCase, BambooParser):

    def test_database_init(self):
        parser = BambooParser(url=BAMBOO_URL)
        db_init = parser._database_init()
        self.assertEqual(db_init, None)

    def test_get_request(self):
        parser = BambooParser(url=BAMBOO_URL)
        response = parser._get_employees(url=BAMBOO_URL)
        self.assertNotEqual(response, False, msg='HTTP Request is FAILED')

    def test_available_fields(self):
        parser = BambooParser(url=BAMBOO_URL)
        fields = parser.available_fields()
        self.assertEqual(type(fields), type(''), msg='Some fields may be changed -> check XML file')

    def test_parser(self):
        parser = BambooParser(url=BAMBOO_URL)
        parsed = parser.bamboo_parse()
        self.assertEqual(parsed, None, msg='Cannot parse some fields -> check XML file')

    def test_writing(self):
        parser = BambooParser(url=BAMBOO_URL)
        emp = parser.bamboo_parse()
        session = parser._write_session(emp)
        self.assertEqual(session, None, msg='Something wrong with file writing')


if __name__ == '__main__':
    unittest.main()
