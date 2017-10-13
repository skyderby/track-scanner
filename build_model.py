import pandas
import os
from sklearn import svm
from sklearn.externals import joblib

directory = os.listdir(os.fsencode('./train'))
dataset = pandas.concat([
    pandas.read_csv('./train/' + os.fsdecode(name)) for name in directory
])

dataset['h_speed'] = (dataset['velN']**2 + dataset['velE']**2) ** 0.5 * 3.6
dataset['v_speed'] = dataset['velD'] * 3.6

dataset = dataset.sample(frac=1)
X = dataset[['h_speed', 'v_speed']]
y = dataset['class']

clf = svm.SVC(kernel='rbf', gamma=0.001, C=1.0, decision_function_shape='ovo')
clf.fit(X, y)

joblib.dump(clf, 'model.pkl')
