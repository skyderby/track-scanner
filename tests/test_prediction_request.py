from tracksegmenter import app
import unittest
from flask import json


class TestPredictionRequest(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def request_data(self, filename):
        with open('data/test/' + filename) as f:
            return f.read()

    def test_prediction_wind_affected(self):
        resp = self.app.post(
            '/prediction',
            data=self.request_data('#7990 15-56-18.CSV')
        )

        data = json.loads(resp.data)

        expected = {
            'activity': 'skydive',
            'flight_starts_at': '2016-10-23T21:07:59.650',
            'deploy_at': '2016-10-23T21:09:56.200'
        }

        self.assertEqual(data, expected)
