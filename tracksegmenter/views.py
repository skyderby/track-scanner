from tracksegmenter import app
from flask import request, jsonify, render_template
from tracksegmenter.processing import DataProcessor, NoFlightFoundError, InvalidFlightDataError


@app.route('/api/v1/scan', methods=['POST'])
def prediction():
    posted_data = request.data.decode('utf-8')

    try:
        processing_result = DataProcessor(posted_data).call()
    except NoFlightFoundError:
        return jsonify({'error': 'no flight data'}), 422
    except InvalidFlightDataError:
        return jsonify({'error': 'invalid flight data'}), 422

    return jsonify(processing_result)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/model/overview', methods=['GET'])
def model_overview():
    return render_template('model_overview.html')


@app.route('/model/test', methods=['GET'])
def model_test():
    return render_template('model_test.html')
