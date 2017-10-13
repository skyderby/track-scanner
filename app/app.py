from flask import Flask, request
import pandas
from sklearn.externals import joblib
from io import StringIO

app = Flask(__name__)


@app.route('/prediction', methods=['POST'])
def prediction():
    clf = joblib.load('model.pkl')
    posted_data = request.data.decode('utf-8')
    df = pandas.read_csv(StringIO(posted_data))
    df['class'] = clf.predict(df[['h_speed', 'v_speed']])

    result = StringIO()
    df.to_csv(result, index=False)

    return result.getvalue()


if __name__ == '__main__':
    app.run()
