import pandas
import numpy as np
from io import StringIO
from sklearn.externals import joblib
from datetime import timedelta
from .preprocessing import Preprocessor


flight_classifier = joblib.load('model/flight.pkl')
flight_scaler = joblib.load('model/flight_scaler.pkl')


class NoFlightFoundError(Exception):
    """ Exception raised if no flight found in processed data """
    pass


class DataProcessor:
    def __init__(self, string_data):
        self.string_data = string_data

    def call(self):
        self.read_data()
        self.preprocess_data()
        self.find_flight_start()
        self.trim_from_landing()
        self.find_deploy()

        return self.processing_result()

    def read_data(self):
        self.raw_df = pandas.read_csv(StringIO(self.string_data), header=0)

    def preprocess_data(self):
        self.preprocessed_df = Preprocessor(self.raw_df).call()

    def find_flight_start(self):
        df = self.preprocessed_df

        V_SPEED_THRESHOLD = 35  # km/h
        passed_treshold = (
            df['v_speed']
            .rolling(window='3s')
            .mean()
            .apply(lambda x: x > V_SPEED_THRESHOLD)
        )
        not_in_aircraft = df['is_aircraft'] == 0

        df['flight_started'] = passed_treshold & not_in_aircraft

        flight_start_found = (
            df[df['flight_started'] == True].count()['flight_started'] > 1
        )

        if flight_start_found:
            self.flight_starts_at = (
                df['flight_started'].ne(False).idxmax() -
                timedelta(seconds=2.5)
            )
        else:
            raise NoFlightFoundError

    def trim_from_landing(self):
        df = self.preprocessed_df[self.flight_starts_at:].copy()

        landing = self.find_landing(df)
        if landing is not None:
            df = df[:landing + timedelta(seconds=3)]

        self.trimmed_df = df

    def find_deploy(self):
        def group_details(x):
            return pandas.Series({
                'class': x.iloc[0]['is_flight'],
                'segment_start': x.index[0],
                'segment_end': x.index[-1],
                'duration_s': x.index[-1] - x.index[0]
            })

        df = self.trimmed_df.copy()

        df = df[self.flight_starts_at:]
        features_list = ['h_speed', 'v_speed']

        df[features_list] = flight_scaler.transform(df[features_list])
        df['is_flight'] = flight_classifier.predict(df[features_list])
        df['is_flight'] = df['is_flight'].rolling(window='5s').median()

        df['cl_weight'] = np.where(df['is_flight'] == 1.0, 3.0, -1.0)
        df['weight'] = df['cl_weight'].cumsum()

        self.deploy_at = df['weight'].idxmax()
        #self.deploy_at = df['is_flight'].eq(1).cumsum().idxmax()
        # df['group'] = df['is_flight'].diff().ne(0).cumsum()
        # segments = (df.groupby('group')
        #               .apply(group_details)
        #               .sort_values('segment_start'))
        # idx = segments[segments['class'] == 1.0]['duration_s'].idxmax()
        # segments = segments[segments['class'] == 0.0]
        # segments = segments[segments['duration_s'] > timedelta(seconds=20)]
        # if segments.empty:
        #     self.deploy_at = df.index[-1]
        # else:
        #     self.deploy_at = segments.iloc[0]['segment_start']

        # self.deploy_at = segments.loc[idx].segment_end + timedelta(seconds=2)

    def processing_result(self):
        def format_date(date):
            return date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        return {
            'flight_starts_at': format_date(self.flight_starts_at),
            'deploy_at':        format_date(self.deploy_at)
        }

    def find_landing(self, df):
        def group_details(x):
            return pandas.Series({
                'class': x.iloc[0].is_ground,
                'segment_start': x.index[0],
                'segment_end': x.index[-1],
                'duration_s': x.index[-1] - x.index[0]
            })

        df['group'] = df['is_ground'].diff().ne(0).cumsum()
        segments = df.groupby('group').apply(group_details)
        segments = segments[segments['class'] == 1.0]
        segments = segments[segments['duration_s'] > timedelta(seconds=30)]

        if segments.empty:
            return None
        else:
            return segments.iloc[0]['segment_start']
