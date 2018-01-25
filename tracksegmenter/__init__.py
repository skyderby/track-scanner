from flask import Flask

import warnings
warnings.filterwarnings(action="ignore",
                        module="scipy",
                        message="^internal gelsd")

app = Flask(__name__)

import tracksegmenter.logging  #noqa
import tracksegmenter.views    #noqa
