from tracksegmenter import app
import unittest
from flask import json
from datetime import timedelta
from dateutil import parser as date_parser


class TestAPI_V1(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def request_data(self, filename):
        with open('data/test/' + filename) as f:
            return f.read()

    def test_prediction_wind_affected(self):
        resp = self.app.post(
            '/api/v1/scan',
            data=self.request_data('#7990 15-56-18.CSV')
        )

        data = json.loads(resp.data)

        expected_start = date_parser.parse('2016-10-23T21:07:59.000Z')
        actual_start = date_parser.parse(data['flight_starts_at'])

        expected_deploy = date_parser.parse('2016-10-23T21:09:56.000Z')
        actual_deploy = date_parser.parse(data['deploy_at'])

        self.assertEqual('skydive', data['activity'])
        self.assertAlmostEqual(expected_start,
                               actual_start,
                               delta=timedelta(seconds=1))
        self.assertAlmostEqual(expected_deploy,
                               actual_deploy,
                               delta=timedelta(seconds=1))

    def test_prediction_with_swoop(self):
        resp = self.app.post(
            '/api/v1/scan',
            data=self.request_data('#703 14-41-39.CSV')
        )

        data = json.loads(resp.data)

        expected_start = date_parser.parse('2014-08-07 14:50:14.400Z')
        actual_start = date_parser.parse(data['flight_starts_at'])

        expected_deploy = date_parser.parse('2014-08-07 14:52:02.800Z')
        actual_deploy = date_parser.parse(data['deploy_at'])

        self.assertEqual('skydive', data['activity'])
        self.assertAlmostEqual(expected_start,
                               actual_start,
                               delta=timedelta(seconds=1))
        self.assertAlmostEqual(expected_deploy,
                               actual_deploy,
                               delta=timedelta(seconds=1))

    def test_no_flight_data(self):
        with open('tests/fixtures/flysight_warmup.csv') as f:
            request_data = f.read()

        resp = self.app.post('/api/v1/scan', data=request_data)
        data = json.loads(resp.data)
        expected = {'error': 'no flight data'}

        self.assertEqual(expected, data)
