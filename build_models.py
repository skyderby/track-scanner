#!/usr/bin/env python

import pandas
import numpy as np
from sklearn import svm
from sklearn import preprocessing
from sklearn.tree import DecisionTreeClassifier
from sklearn.externals import joblib
from scipy.signal import savgol_filter

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt  # noqa

import warnings  # noqa
warnings.filterwarnings(action="ignore",
                        module="scipy",
                        message="^internal gelsd")


class ModelBuilderMixin:
    # All train files are 5Hz, window size is 3 sec
    FREQ = 5
    WINDOW = FREQ * 3

    def preprocess_file(self, df):
        df['h_speed'] = (df['velN']**2 + df['velE']**2) ** 0.5 * 3.6
        df['v_speed'] = df['velD'] * 3.6
        df['h_speed'] = savgol_filter(df['h_speed'],
                                      self.WINDOW,
                                      0,
                                      mode='nearest')

        df['v_speed'] = savgol_filter(df['v_speed'],
                                      self.WINDOW,
                                      0,
                                      mode='nearest')

        return df


class FlightModelBuilder(ModelBuilderMixin):
    def __init__(self):
        self.features_list = ['h_speed', 'v_speed']
        self.df = self.train_dataset()

    def call(self):
        self.train_model()
        self.save_model()
        self.save_model_plot()
        self.save_data_distribution_plot()

    def train_model(self):
        print('--- Training model')

        # Filter only by Flight and Canopy classes
        self.df = self.df.loc[self.df['class'].isin([2, 3])]

        self.df['is_flight'] = (self.df['class'] == 2).astype('float')

        self.df[self.features_list] = (
            preprocessing.scale(self.df[self.features_list])
        )

        X = self.df[self.features_list]
        y = self.df['is_flight']

        self.clf = svm.SVC(kernel='rbf', gamma=1.0, C=0.1)
        self.clf.fit(X, y)

    def save_model(self):
        print('--- Saving model to file')

        joblib.dump(self.clf, 'flight_model.pkl')

    def save_model_plot(self):
        print('--- Saving SVM plot')

        plt.figure()
        plt.title('SVM RBF Kernel')

        plt.scatter(
            self.df['h_speed'],
            self.df['v_speed'],
            c=self.df['is_flight'],
            zorder=10,
            s=2
        )

        x_min, x_max = self.df['h_speed'].min(), self.df['h_speed'].max()
        y_min, y_max = self.df['v_speed'].min(), self.df['v_speed'].max()

        h = 0.01
        XX, YY = np.meshgrid(np.arange(x_min, x_max, h),
                             np.arange(y_min, y_max, h))

        Z = self.clf.predict(np.c_[XX.ravel(), YY.ravel()]).reshape(XX.shape)
        ax = plt.gca()
        ax.pcolormesh(XX, YY, Z, alpha=0.1)

        plt.savefig('tracksegmenter/static/svm_plot.png')

    def save_data_distribution_plot(self):
        print('--- Saving value distribution plot')
        plt.figure()
        plt.title('Examples by class')
        map_dict = {0: 'Canopy', 1: 'Flight'}
        series = self.df['is_flight'].map(map_dict)

        values = series.value_counts()
        values.plot(kind='bar', colormap='Set2')
        plt.xticks(rotation=0)
        plt.savefig('tracksegmenter/static/values_plot.png')

    def train_dataset(self):
        from glob import glob

        directory = glob('./data/train/flight/*.csv')
        train_files = list()

        for name in directory:
            df = pandas.read_csv(name)
            df = self.preprocess_file(df)
            train_files.append(df)

        return pandas.concat(train_files)


class AircraftModelBuilder(ModelBuilderMixin):
    def __init__(self):
        self.df = self.train_dataset()

    def call(self):
        self.train_model()
        self.save_model()

    def train_model(self):
        print('--- Training model')

        X = self.df[['h_speed', 'v_speed', 'gr']]
        y = self.df['is_aircraft']

        self.clf = DecisionTreeClassifier(criterion='entropy', max_depth=5)
        self.clf.fit(X, y)

    def save_model(self):
        print('--- Saving model to file')

        joblib.dump(self.clf, 'aircraft_model.pkl')

    def train_dataset(self):
        from glob import glob

        directory = glob('./data/train/aircraft/*.csv')
        train_files = list()

        for name in directory:
            df = pandas.read_csv(name)
            df = self.preprocess_file(df)
            train_files.append(df)

        return pandas.concat(train_files)

    def preprocess_file(self, df):
        df = super().preprocess_file(df)

        df['is_aircraft'] = (df['class'] == 4).astype('float')
        df['gr'] = df['h_speed'] / df['v_speed']
        df['gr'] = df['gr'].replace([np.inf, -np.inf], np.nan).bfill()

        return df


class GroundModelBuilder(ModelBuilderMixin):
    def __init__(self):
        self.df = self.train_dataset()

    def call(self):
        self.train_model()
        self.save_model()

    def train_model(self):
        print('--- Training model')

        X = self.df[['h_speed', 'v_speed', 'altitude_chng']]
        y = self.df['is_ground']

        self.clf = DecisionTreeClassifier(criterion='entropy', max_depth=5)
        self.clf.fit(X, y)

    def save_model(self):
        print('--- Saving model to file')

        joblib.dump(self.clf, 'ground_model.pkl')

    def train_dataset(self):
        from glob import glob

        directory = glob('./data/train/ground/*.csv')
        train_files = list()

        for name in directory:
            df = pandas.read_csv(name)
            df = self.preprocess_file(df)
            train_files.append(df)

        return pandas.concat(train_files)

    def preprocess_file(self, df):
        df = super().preprocess_file(df)

        df['is_ground'] = (df['class'] == 1).astype('float')
        df['altitude_chng'] = (df['hMSL'].rolling(window=25).std()).bfill()

        return df


if __name__ == '__main__':
    print('### Flight model')
    FlightModelBuilder().call()

    print('\n### Aircraft model')
    AircraftModelBuilder().call()

    print('\n### Ground model')
    GroundModelBuilder().call()
