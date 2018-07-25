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


@app.route('/', methods=['GET'])
def index():
    import glob
    test_files = [f.rpartition('/')[2] for f in glob.glob('./data/test/*.csv')]

    return render_template('index.html', figures=test_files)


@app.route('/model/overview', methods=['GET'])
def model_overview():
    return render_template('model_overview.html')


@app.route('/track_plot/<track_file_name>', methods=['GET'])
def track_plot(track_file_name):
    from io import BytesIO
    from flask import make_response
    import matplotlib
    matplotlib.use('agg')

    import pandas
    import matplotlib.pyplot as plt

    with open('./data/test/' + track_file_name, 'r') as f:
        string_data = f.read()

    data_processor = DataProcessor(string_data)

    try:
        result = data_processor.call()
    except NoFlightFoundError:
        return jsonify({'error': 'no flight data'}), 422

    df = data_processor.preprocessed_df

    plt.figure()
    plt.plot(df['h_speed'], linewidth=0.5)
    plt.plot(df['v_speed'], linewidth=0.5)
    plt.plot(df['is_ground'] * -10)
    plt.plot(df['is_aircraft'] * -20)
    plt.plot(df['flight_started'] * -50)
    plt.axvline(x=data_processor.flight_starts_at, color='green', linewidth=1)
    plt.axvline(x=data_processor.deploy_at, color='red', linewidth=1)

    plot_output = BytesIO()
    plt.savefig(plot_output, format='png')

    response = make_response(plot_output.getvalue())
    response.headers['Content-Type'] = 'image/png'

    return response
