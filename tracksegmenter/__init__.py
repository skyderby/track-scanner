from flask import Flask
from sklearn.externals import joblib

app = Flask(__name__)
classifier = joblib.load('model.pkl')

import tracksegmenter.logging
import tracksegmenter.views
