import glob
import pandas
from .preprocessing import preprocess_data
from .feature_extraction import extract_features

features_list = ['h_speed', 'v_speed']


def train_dataset():
    directory = glob.glob('./data/train/*.csv')
    train_files = list()
    for name in directory:
        df = pandas.read_csv(name)
        df = preprocess_data(df)
        df = extract_features(df)
        train_files.append(df)

    return pandas.concat(train_files)
