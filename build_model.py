#!/usr/bin/env python

from sklearn import svm
from sklearn.externals import joblib
from tracksegmenter.data_flow import features_list, train_dataset

import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt  # noqa

df = train_dataset()

print('--- Training model')

X = df[features_list]
y = df['class']

clf = svm.SVC(kernel='rbf', gamma=0.001, C=1.0, decision_function_shape='ovo')
clf.fit(X, y)

print('--- Saving model to file')

joblib.dump(clf, 'model.pkl')

print('--- Saving SVM plot')

plt.figure()
plt.title('SVM RBF Kernel')

plt.scatter(df['h_speed'], df['v_speed'], c=y, zorder=10, s=2)

x_min, x_max = df['h_speed'].min(), df['h_speed'].max()
y_min, y_max = df['v_speed'].min(), df['v_speed'].max()

h = 1
XX, YY = np.meshgrid(np.arange(x_min, x_max, h),
                     np.arange(y_min, y_max, h))

Z = clf.predict(np.c_[XX.ravel(), YY.ravel()]).reshape(XX.shape)
ax = plt.gca()
ax.pcolormesh(XX, YY, Z, alpha=0.1)

plt.savefig('tracksegmenter/static/svm_plot.png')

print('--- Saving value distribution plot')
plt.figure()
plt.title('Examples by class')
plt.hist(df['class'])
plt.savefig('tracksegmenter/static/values_plot.png')
