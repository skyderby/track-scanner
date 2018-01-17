from tracksegmenter import app
import unittest
from flask import json
from datetime import datetime, timedelta


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

        date_format = '%Y-%m-%dT%H:%M:%S.%f'
        expected_start = datetime.strptime('2016-10-23T21:07:59.000', date_format)
        actual_start = datetime.strptime(data['flight_starts_at'], date_format)

        expected_deploy = datetime.strptime('2016-10-23T21:09:56.000', date_format)
        actual_deploy = datetime.strptime(data['deploy_at'], date_format)

        self.assertEqual('skydive', data['activity'])
        self.assertAlmostEqual(expected_start,
                               actual_start,
                               delta=timedelta(seconds=1))
        self.assertAlmostEqual(expected_deploy,
                               actual_deploy,
                               delta=timedelta(seconds=1))
