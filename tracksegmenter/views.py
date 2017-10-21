from tracksegmenter import app, classifier
from flask import request, jsonify
import pandas
from io import StringIO

class_mappings = {
    1: 'ground',
    2: 'flight',
    3: 'canopy',
    4: 'aircraft'
}

@app.route('/prediction', methods=['POST'])
def prediction():
    posted_data = request.data.decode('utf-8')
    df = pandas.read_csv(StringIO(posted_data))
    df['class'] = classifier.predict(df[['h_speed', 'v_speed']])

    df['group'] = df['class'].diff().ne(0).cumsum()
    groups = df.groupby('group')['group'].apply(lambda x: x.index)

    res = list()
    for x in groups:
        values = df.iloc[x]
        first, last = values.iloc[0], values.iloc[-1]

        res.append({
            'type':     class_mappings[first['class']],
            'start':    round(first['fl_time'].item(), 1),
            'end':      round(last['fl_time'].item(), 1),
            'duration': round((last['fl_time'] - first['fl_time']).item(), 1)
        })

    return jsonify(res)
