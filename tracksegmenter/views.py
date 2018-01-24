from tracksegmenter import app
from flask import request, jsonify, render_template
from tracksegmenter.processing import DataProcessor, NoFlightFoundError


@app.route('/api/v1/scan', methods=['POST'])
def prediction():
    posted_data = request.data.decode('utf-8')

    try:
        processing_result = DataProcessor(posted_data).call()
    except NoFlightFoundError:
        return jsonify({'error': 'no flight data'}), 422

    return jsonify(processing_result)

    # flight_start = (df['flight_started'].ne(False).idxmax() -
    #                 timedelta(seconds=2.55))
    # df = df[flight_start:]
    #
    # df[features_list] = preprocessing.minmax_scale(df[features_list])
    #
    # df['class'] = classifier.predict(df[features_list])
    #
    # def group_details(x):
    #     return pandas.Series({
    #         'class': x.iloc[0]['class'],
    #         'size': len(x.index),
    #         'segment_end': x.index[-1]
    #     })
    #
    # df['group'] = df['class'].diff().ne(0).cumsum()
    # segments = df.groupby('group').apply(group_details)
    # idx = segments[segments['class'] == 1.0]['size'].idxmax()
    # flight_end = segments.loc[idx].segment_end
    #
    # def format_datetime(date):
    #     return date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    #


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/model/overview', methods=['GET'])
def model_overview():
    return render_template('model_overview.html')


@app.route('/model/test', methods=['GET'])
def model_test():
    return render_template('model_test.html')
