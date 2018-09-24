import unittest
import bamboohr_to_database as master


class TestRequests(unittest.TestCase):

    def test_database_init(self):
        db_init = master.database_init()
        self.assertEqual(db_init, )

    def test_get_request(self):
        response = master.bamboo_request(url=master.BAMBOO_URL)
        self.assertNotEqual(response, False, msg='HTTP Request is FAILED')

    def test_available_fields(self):
        fields = master.available_fields()
        self.assertEqual(type(fields), type(''), msg='Some fields may be changed -> check XML file')

    def test_parser(self):
        parser = master.bamboo_parse()
        self.assertEqual(parser, None, msg='Cannot parse some fields -> check XML file')

    def test_writing(self):
        session = master.write_session()
        self.assertEqual(session, None, msg='Something wrong with file writing')


if __name__ == '__main__':
    unittest.main()
