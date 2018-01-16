#!/usr/bin/env python

import pandas
import numpy as np
from sklearn import svm
from sklearn import preprocessing
from sklearn.externals import joblib
from scipy.signal import savgol_filter

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt  # noqa


def train_dataset(path_prefix=None):
    from glob import glob

    if path_prefix is None:
        path_prefix = '.'

    directory = glob(path_prefix + '/data/train/*.csv')
    train_files = list()

    # All train files are 5Hz, window size is 3 sec
    freq = 5
    window = freq * 3

    for name in directory:
        df = pandas.read_csv(name)
        df['h_speed'] = (df['velN']**2 + df['velE']**2) ** 0.5
        df['v_speed'] = df['velD']
        df['h_speed'] = savgol_filter(df['h_speed'], window, 0, mode='nearest')
        df['v_speed'] = savgol_filter(df['v_speed'], window, 0, mode='nearest')

        train_files.append(df)

    return pandas.concat(train_files)


class ModelBuilder:
    def __init__(self):
        self.features_list = ['h_speed', 'v_speed']
        self.df = train_dataset()

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
            preprocessing.minmax_scale(self.df[self.features_list])
        )

        X = self.df[self.features_list]
        y = self.df['is_flight']

        self.clf = svm.SVC(kernel='rbf', gamma=1.0, C=100)
        self.clf.fit(X, y)

    def save_model(self):
        print('--- Saving model to file')

        joblib.dump(self.clf, 'model.pkl')

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
        plt.hist(self.df['is_flight'])
        plt.savefig('tracksegmenter/static/values_plot.png')


if __name__ == '__main__':
    ModelBuilder().call()
