import pandas as pd
import os
import numpy as np
os.makedirs('data/processed', exist_ok=True)

def detect_spikes(df, column, window=7, threshold=5):

    
    rolling_median = df[column].rolling(
        window=window,
        center=True,
        min_periods=3
    ).median()

  
    deviation = (df[column] - rolling_median).abs()

    rolling_mad = deviation.rolling(
        window=window,
        center=True,
        min_periods=3
    ).median()

    rolling_mad = rolling_mad.replace(0, np.nan)


    score = 0.6745 * deviation / rolling_mad

  
    return score > threshold


def remove_slack(df, force_column='force_N', threshold_ratio=0.02):

   
    max_force = df[force_column].max()

    
    threshold = max_force * threshold_ratio

    
    valid_points = df[force_column] > threshold

   
    if not valid_points.any():
        print("No valid tensile loading region found")
        return df.iloc[0:0].copy()

    start_index = valid_points[valid_points].index[0]

    
    df = df.loc[start_index:].copy()


    df.reset_index(drop=True, inplace=True)

    return df


specimens_df = pd.read_csv('data/specimens.csv')

for test_id in specimens_df['test_id']:
    df = pd.read_csv(f'data/raw/{test_id}.csv')
    
    
    if 'displacement_m' in df.columns:
        df['displacement_mm'] = df['displacement_m'] * 1000
        df.drop(columns=['displacement_m'], inplace=True)
    elif 'displacement_mm' in df.columns:
        pass
    else:
        print("Displacement column not found")
        continue

    df =df.drop_duplicates()
    df = df.dropna(subset=['force_N', 'displacement_mm'])

    df['force_spike'] = detect_spikes(df, 'force_N')

    df['displacement_spike'] = detect_spikes(
    df, 'displacement_mm'
            )

    df['is_spike'] = (
    df['force_spike'] | df['displacement_spike']
    )
    df = df[~df['is_spike']].copy()

    df.drop(
    columns=['force_spike', 'displacement_spike', 'is_spike'],
    inplace=True
    )
    df = remove_slack(df)


    df.to_csv(
    f'data/processed/{test_id}.csv',
    index=False
    )




