import pandas


def preprocess_data(df):
    df['time'] = pandas.to_datetime(df['time'])
    # df.set_index('time', inplace=True)

    df['h_speed'] = (df['velN']**2 + df['velE']**2) ** 0.5 * 3.6
    df['v_speed'] = df['velD'] * 3.6

    return df
