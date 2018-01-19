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

    def group_details(x):
        return pandas.Series({
            'class': x.iloc[0]['class'],
            'size': len(x.index),
            'segment_end': x.index[-1]
        })

    df['group'] = df['class'].diff().ne(0).cumsum()
    segments = df.groupby('group').apply(group_details)
    idx = segments[segments['class'] == 1.0]['size'].idxmax()
    flight_end = segments.loc[idx].segment_end

    def format_datetime(date):
        return date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    res = {
        'activity':         'skydive',
        'flight_starts_at': format_datetime(flight_start),
        'deploy_at':        format_datetime(flight_end)
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
