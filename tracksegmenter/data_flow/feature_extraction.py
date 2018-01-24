import pandas
from scipy.signal import savgol_filter


def extract_features(df):
    df['time'] = pandas.to_datetime(df['time'])
    df['prev_time'] = df.shift()['time']
    df['time_diff'] = df['time'] - df['prev_time']

    most_used_freq = df['time_diff'].value_counts().index.values[0]
    freq = 1000 / most_used_freq.astype('timedelta64[ms]').astype('float')
    window = freq * 3

    if window % 2 == 0:
        window += 1

    df.set_index('time', inplace=True)

    if 'h_speed' not in df.columns:
        df['h_speed'] = (df['velN']**2 + df['velE']**2) ** 0.5 * 3.6

    if 'v_speed' not in df.columns:
        df['v_speed'] = df['velD'] * 3.6

    df['h_speed'] = savgol_filter(df['h_speed'], window, 0, mode='nearest')
    df['v_speed'] = savgol_filter(df['v_speed'], window, 0, mode='nearest')

    df['v_speed_chg_ms'] = (df['v_speed'] - df['v_speed'].shift().bfill()) / 3.6
    df['v_acceleration'] = (
        df['v_speed_chg_ms'] *
        (1000 / df['time_diff'].astype('timedelta64[ms]').astype('float'))
    )

    V_ACCEL_THRESHOLD = 2.5  # m/s^2
    df['flight_started'] = (
        df['v_acceleration']
        .rolling(window='3s')
        .mean()
        .apply(lambda x: x > V_ACCEL_THRESHOLD)
    )

    return df
