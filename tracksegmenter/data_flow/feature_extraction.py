import pandas

def extract_features(df):
    df['v_speed_change'] = df['v_speed'].pct_change().fillna(0).abs()
    df['v_speed_change'] = pandas.rolling_median(df['v_speed_change'], window=3, center=True).fillna(0)


    return df
