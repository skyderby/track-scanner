from tracksegmenter import app
from flask import request, jsonify
import pandas
from sklearn.externals import joblib
from io import StringIO

class_mappings = {
    1: 'ground',
    2: 'flight',
    3: 'canopy',
    4: 'aircraft'
}

@app.route('/prediction', methods=['POST'])
def prediction():
    clf = joblib.load('model.pkl')
    posted_data = request.data.decode('utf-8')
    df = pandas.read_csv(StringIO(posted_data))
    df['class'] = clf.predict(df[['h_speed', 'v_speed']])

    df['group'] = df['class'].diff().ne(0).cumsum()
    groups = df.groupby('group')['group'].apply(lambda x: x.index)

    res = list()
    for x in groups:
        values = df.iloc[x]
        first, last = values.iloc[0], values.iloc[-1]

        group_name = class_mappings[first['class']]
        group = dict()
        group[group_name]  = {'start': first['fl_time'].item(), 'end': last['fl_time'].item()}
        res.append(group)

    return jsonify(res)
