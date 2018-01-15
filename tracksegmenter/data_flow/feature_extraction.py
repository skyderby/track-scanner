import pandas
from scipy.signal import savgol_filter


def extract_features(df):
    df['time'] = pandas.to_datetime(df['time'])
    df['prev_time'] = df.shift()['time']
    df['time_diff'] = df['time'] - df['prev_time']

    most_used_freq = df['time_diff'].value_counts().index.values[0]
    freq = 1000 / most_used_freq.astype('timedelta64[ms]').astype('float')
    window = freq * 3

    df.set_index('time', inplace=True)

    if 'h_speed' not in df.columns:
        df['h_speed'] = (df['velN']**2 + df['velE']**2) ** 0.5

    if 'v_speed' not in df.columns:
        df['v_speed'] = df['velD']

    df['h_speed'] = savgol_filter(df['h_speed'], window, 0, mode='nearest')
    df['v_speed'] = savgol_filter(df['v_speed'], window, 0, mode='nearest')

    V_SPEED_THRESHOLD = 7  # m/s
    df['flight_started'] = (
        df['v_speed']
        .rolling(window='3s')
        .mean()
        .apply(lambda x: x > V_SPEED_THRESHOLD)
    )

    return df
