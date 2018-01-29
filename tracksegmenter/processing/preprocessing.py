import pandas
import numpy as np
from scipy.signal import savgol_filter
from sklearn.externals import joblib

aircraft_classifier = joblib.load('model/aircraft.pkl')
ground_classifier = joblib.load('model/ground.pkl')


class Preprocessor:
    def __init__(self, df):
        self.df = df

    def call(self):
        df = self.df.copy()
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

        df['altitude_std'] = (df['hMSL'].rolling(window='5s').std()).bfill()

        df['is_aircraft'] = aircraft_classifier.predict(
            df[['h_speed', 'v_speed', 'gr']]
        )
        df['is_aircraft'] = df['is_aircraft'].rolling(window='15s').median()

        df['is_ground'] = ground_classifier.predict(
            df[['h_speed', 'v_speed', 'altitude_std']]
        )
        df['is_ground'] = df['is_ground'].rolling(window='5s').median()

        return df

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
