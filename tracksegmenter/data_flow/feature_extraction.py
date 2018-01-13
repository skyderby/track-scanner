
def extract_features(df):
    df['v_speed_change'] = df['v_speed'].pct_change().fillna(0).abs()
    df['v_speed_change'] = (
        df['v_speed_change'].rolling(window=3, center=True)
                            .median()
                            .fillna(0)
    )

    return df
