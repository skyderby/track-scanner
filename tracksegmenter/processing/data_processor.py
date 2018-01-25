import pandas
import numpy as np
from io import StringIO
from sklearn import preprocessing
from sklearn.externals import joblib
from scipy.signal import savgol_filter
from datetime import timedelta


flight_classifier = joblib.load('flight_model.pkl')
aircraft_classifier = joblib.load('aircraft_model.pkl')


class NoFlightFoundError(Exception):
    """ Exception raised if no flight found in processed data """
    pass


class DataProcessor:
    def __init__(self, string_data):
        self.string_data = string_data

    def call(self):
        self.read_data()
        self.preprocess_data()
        self.trim_data()
        self.find_flight_start()
        self.ensure_flight_recorded()
        self.find_deploy()

        return self.processing_result()

    def read_data(self):
        self.raw_df = pandas.read_csv(StringIO(self.string_data), header=0)

    def preprocess_data(self):
        df = self.raw_df.copy()
        df['time'] = pandas.to_datetime(df['time'])
        df['prev_time'] = df.shift()['time']
        df['time_diff'] = df['time'] - df['prev_time']

        window = self.window_size(df)

        df.set_index('time', inplace=True)

        if 'h_speed' not in df.columns:
            df['h_speed'] = (df['velN']**2 + df['velE']**2) ** 0.5 * 3.6

        if 'v_speed' not in df.columns:
            df['v_speed'] = df['velD'] * 3.6

        df['h_speed'] = savgol_filter(df['h_speed'], window, 0, mode='nearest')
        df['v_speed'] = savgol_filter(df['v_speed'], window, 0, mode='nearest')

        df['gr'] = df['h_speed'] / df['v_speed']
        df['gr'] = df['gr'].replace([np.inf, -np.inf], np.nan).bfill()

        self.preprocessed_df = df

    def trim_data(self):
        df = self.preprocessed_df.copy()

        aircraft_exit = self.find_aircraft_exit(df)
        if aircraft_exit is not None:
            df = df[aircraft_exit - timedelta(seconds=3):]

        landing = self.find_landing(df)
        if landing is not None:
            df = df[:landing + timedelta(seconds=3)]

        self.trimmed_df = df

    def ensure_flight_recorded(self):
        if self.flight_starts_at is None:
            raise NoFlightFoundError

    def find_flight_start(self):
        df = self.trimmed_df.copy()

        V_SPEED_THRESHOLD = 35  # km/h
        df['flight_started'] = (
            df['v_speed']
            .rolling(window='3s')
            .mean()
            .apply(lambda x: x > V_SPEED_THRESHOLD)
        )

        if df[df['flight_started'] == True].count()['flight_started'] > 1:
            self.flight_starts_at = (
                df['flight_started'].ne(False).idxmax() -
                timedelta(seconds=2.5)
            )
        else:
            self.flight_starts_at = None

    def find_deploy(self):
        def group_details(x):
            return pandas.Series({
                'class': x.iloc[0]['class'],
                'size': len(x.index),
                'segment_end': x.index[-1]
            })

        df = self.trimmed_df.copy()

        df = df[self.flight_starts_at:]
        features_list = ['h_speed', 'v_speed']

        df[features_list] = preprocessing.scale(df[features_list])
        df['class'] = flight_classifier.predict(df[features_list])

        df['group'] = df['class'].diff().ne(0).cumsum()
        segments = df.groupby('group').apply(group_details)
        idx = segments[segments['class'] == 1.0]['size'].idxmax()

        self.deploy_at = segments.loc[idx].segment_end + timedelta(seconds=2)

    def processing_result(self):
        def format_date(date):
            return date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        return {
            'flight_starts_at': format_date(self.flight_starts_at),
            'deploy_at':        format_date(self.deploy_at)
        }

    def find_aircraft_exit(self, df):
        df['is_aircraft'] = aircraft_classifier.predict(
            df[['h_speed', 'v_speed', 'gr']]
        )
        df['is_aircraft'] = df['is_aircraft'].rolling(window='5s').median()

        def group_details(x):
            return pandas.Series({
                'class': x.iloc[0].is_aircraft,
                'segment_start': x.index[0],
                'segment_end': x.index[-1],
                'duration_s': x.index[-1] - x.index[0]
            })

        df['group'] = df['is_aircraft'].diff().ne(0).cumsum()
        segments = (df.groupby('group')
                      .apply(group_details)
                      .sort_values('duration_s'))
        segments = segments[segments['class'] == 1.0]
        segments = segments[segments['duration_s'] > timedelta(minutes=1)]

        if segments.empty:
            return None
        else:
            return segments.iloc[0]['segment_end']

    def find_landing(self, df):
        pass

    def window_size(self, df):
        window_duration = 3  # seconds
        data_frequency = self.frequency(df['time_diff'])

        window_size = window_duration * data_frequency

        if window_size % 2 == 0:
            window_size += 1

        return window_size

    def frequency(self, time_series):
        most_used_freq = time_series.value_counts().index.values[0]
        frequency = (
            1000 / most_used_freq.astype('timedelta64[ms]').astype('float')
        )

        return frequency
