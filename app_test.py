from app import app
import unittest


class ApplicationTestCase(unittest.TestCase):

    def setUp(self):
        app.app.testing = True
        self.app = app.app.test_client()

    def request_data(self):
        with open('fixtures/request.txt') as f:
            return f.read()

    def test_prediction(self):
        response = self.app.post('/prediction', data=self.request_data())

        print(response.data.decode('utf-8'))

if __name__ == '__main__':
    unittest.main()
