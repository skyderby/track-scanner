from tracksegmenter import app, classifier
from tracksegmenter.data_flow import features_list, extract_features
from flask import request, jsonify, render_template
import pandas
from io import StringIO
from datetime import timedelta
from sklearn import preprocessing


@app.route('/api/v1/scan', methods=['POST'])
def prediction():
    posted_data = request.data.decode('utf-8')
    df = pandas.read_csv(StringIO(posted_data), header=0)
    df = extract_features(df)

    rows_with_flight = df[df['flight_started'] == True]
    flight_started_occurences = rows_with_flight.count()['flight_started']
    if flight_started_occurences < 5:
        return jsonify({'error': 'no flight data'})

    flight_start = (df['flight_started'].ne(False).idxmax() -
                    timedelta(seconds=2.55))
    df = df[flight_start:]

    df[features_list] = preprocessing.minmax_scale(df[features_list])

    df['class'] = classifier.predict(df[features_list])

    flight_end = df['class'].eq(1).cumsum().idxmax()

    res = {
        'activity': 'skydive',
        'flight_starts_at': flight_start.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3],
        'deploy_at': flight_end.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    }

    return jsonify(res)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/model/overview', methods=['GET'])
def model_overview():
    return render_template('model_overview.html')


@app.route('/model/test', methods=['GET'])
def model_test():
    return render_template('model_test.html')
