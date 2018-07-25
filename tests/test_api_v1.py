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

    def track_test(self, filename, start, deploy):
        resp = self.app.post(
            '/api/v1/scan',
            data=self.request_data(filename)
        )

        data = json.loads(resp.data)

        expected_start = date_parser.parse(start)
        actual_start = date_parser.parse(data['flight_starts_at'])

        expected_deploy = date_parser.parse(deploy)
        actual_deploy = date_parser.parse(data['deploy_at'])

        self.assertAlmostEqual(expected_start,
                               actual_start,
                               delta=timedelta(seconds=3))
        self.assertAlmostEqual(expected_deploy,
                               actual_deploy,
                               delta=timedelta(seconds=3))

    def test_prediction_wind_affected(self):
        self.track_test(
            filename='7990_15-56-18.csv',
            start='2016-10-23T21:08:08.000Z',
            deploy='2016-10-23T21:10:03.000Z'
        )

    def test_prediction_with_swoop(self):
        self.track_test(
            filename='703_14-41-39.csv',
            start='2014-08-07 14:50:20.000Z',
            deploy='2014-08-07 14:52:03.000Z'
        )

    def test_prediction_with_high_aircraft_descend(self):
        self.track_test(
            filename='RWL_13-41-49.csv',
            start='2017-06-17 10:02:37.000Z',
            deploy='2017-06-17 10:04:43.000Z'
        )

    def test_prediction_basejump(self):
        self.track_test(
            filename='Base_Big_WS_labeled.csv',
            start='2018-01-10 09:09:12.000Z',
            deploy='2018-01-10 09:09:57.400Z'
        )

    def test_no_flight_data(self):
        with open('tests/fixtures/flysight_warmup.csv') as f:
            request_data = f.read()

        resp = self.app.post('/api/v1/scan', data=request_data)
        data = json.loads(resp.data)
        expected = {'error': 'no flight data'}

        self.assertEqual(422, resp.status_code)
        self.assertEqual(expected, data)
