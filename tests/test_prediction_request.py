from tracksegmenter import app
import unittest
from flask import json


class TestPredictionRequest(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def request_data(self):
        with open('tests/fixtures/request.txt') as f:
            return f.read()

    def test_prediction(self):
        resp = self.app.post('/prediction', data=self.request_data())
        data = json.loads(resp.data)

        expected = [
            {'aircraft': {'start': 1, 'end': 8}},
            {'flight': {'start': 9, 'end': 14}}
        ]

        self.assertEqual(data, expected)
