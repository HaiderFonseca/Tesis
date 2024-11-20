import pandas as pd

def load_and_preprocess_transactions(data_path, previous_time_column, current_time_column):
    """
    Load and preprocess transactions
    """
    data = pd.read_csv(data_path, parse_dates=[previous_time_column, current_time_column], date_format='%Y-%m-%d %H.%M.%S', dtype={'nrc': 'int64', 'delta_enrolled': 'int64'})
    if len(data) == 0:
        data[previous_time_column] = pd.Timestamp.min
        data[current_time_column] = pd.Timestamp.min
        return data
    for time_column in [previous_time_column, current_time_column]:
        # Convert from UTC to UTC-5 (Colombia time)
        data[time_column] = data[time_column] - pd.Timedelta(hours=5)
        # Round down to the nearest 5-minute interval
        data[time_column] = data[time_column].dt.floor('5min')
    return data

def get_initial_time(df, *time_columns):
    """
    Get the initial time
    """
    if len(df) == 0:
        return pd.Timestamp.min
    assert all(df[column].dtype == 'datetime64[ns]' for column in time_columns)
    return df[list(time_columns)].min().min()

def get_time_steps_count(df, natural_tick_interval, *time_columns):
    """
    Get the unique times count
    """
    if len(df) == 0:
        return 0
    assert all(df[column].dtype == 'datetime64[ns]' for column in time_columns)
    return int((df[list(time_columns)].max().max() - df[list(time_columns)].min().min()).total_seconds() // natural_tick_interval) + 1

def apply_transactions(data, transactions, timestamp, current_time_column, nrc_column, delta_enrolled_column):
    """
    Apply transactions to the data in-place and return the number of affected course sections
    """
    current_transactions = transactions[transactions[current_time_column] == timestamp]
    affected_nrcs = current_transactions[nrc_column]
    for course_section in data:
        if int(course_section['nrc']) in affected_nrcs.values:
            delta = current_transactions[current_transactions[nrc_column] == int(course_section['nrc'])][delta_enrolled_column].sum()
            course_section['enrolled'] = str(int(course_section['enrolled']) + delta)
    return affected_nrcs.shape[0]
