#!/usr/bin/env python

import pandas
import numpy as np
from glob import glob
from sklearn import svm
from sklearn import preprocessing
from sklearn.externals import joblib
from scipy.signal import savgol_filter

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt  # noqa


def train_dataset():
    directory = glob('./data/train/*.csv')
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


"""
--- TRAINING MODEL
"""
df = train_dataset()

print('--- Training model')

# Filter only by Flight and Canopy classes
df = df.loc[df['class'].isin([2, 3])]

df['is_flight'] = (df['class'] == 2).astype('float')

features_list = ['h_speed', 'v_speed']
df[features_list] = preprocessing.minmax_scale(df[features_list])

X = df[features_list]
y = df['is_flight']

clf = svm.SVC(kernel='rbf', gamma=0.1, C=1.0)
clf.fit(X, y)

"""
--- SAVING MODEL TO FILE
"""
print('--- Saving model to file')

joblib.dump(clf, 'model.pkl')

"""
--- GENERATING PLOTS
"""
print('--- Saving SVM plot')

plt.figure()
plt.title('SVM RBF Kernel')

plt.scatter(df['h_speed'], df['v_speed'], c=y, zorder=10, s=2)

x_min, x_max = df['h_speed'].min(), df['h_speed'].max()
y_min, y_max = df['v_speed'].min(), df['v_speed'].max()

h = 0.01
XX, YY = np.meshgrid(np.arange(x_min, x_max, h),
                     np.arange(y_min, y_max, h))

Z = clf.predict(np.c_[XX.ravel(), YY.ravel()]).reshape(XX.shape)
ax = plt.gca()
ax.pcolormesh(XX, YY, Z, alpha=0.1)

plt.savefig('tracksegmenter/static/svm_plot.png')

print('--- Saving value distribution plot')
plt.figure()
plt.title('Examples by class')
plt.hist(df['is_flight'])
plt.savefig('tracksegmenter/static/values_plot.png')
