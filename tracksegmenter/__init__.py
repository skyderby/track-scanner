from flask import Flask

app = Flask(__name__)

import tracksegmenter.logging  #noqa
import tracksegmenter.views    #noqa
