import pandas as pd


def zero_fasts(zero_log_file) -> pd.DataFrame:
    """
    Load a log export from Zero Fasting and return the start and end datetimes of each fast.
    DataFrame is reindexed chronologically, oldest to newest, before returned.
    Args:
        zero_log_file: File path of log export.

    Returns: pandas DataFrame of log export.
    """
    # Read in log as a csv
    expected_cols = ['Date', 'Start', 'End', 'Hours', 'Night Eating']
    dtypes = {'End': str, 'Hours': float, 'Night Eating': float}
    fasts = pd.read_csv(zero_log_file,
                        header=0,
                        parse_dates=[['Date', 'Start']],
                        dtype=dtypes,
                        usecols=expected_cols)

    # Clean up DataFrame
    fasts.dropna(subset=['Hours'], inplace=True)  # Drop incomplete fasts (Hours will be NA if incomplete)
    fasts.rename(columns={'Date_Start': 'start_dt'}, inplace=True)  # Rename date parsed column
    fasts = fasts.iloc[::-1].reset_index(drop=True)  # Order by oldest to newest

    # Get end datetime of each fast and add to fasts DataFrame as a new column: 'end_dt'
    end_times = pd.to_datetime(fasts.End).dt.strftime('%H:%M:%S')
    end_time_deltas = pd.to_timedelta(end_times)
    fast_durations = pd.to_timedelta(fasts.Hours, 'H')
    end_dates = (fasts.start_dt + fast_durations).dt.date
    end_dt = pd.to_datetime(end_dates)
    end_dt += end_time_deltas
    fasts['end_dt'] = end_dt

    #  Return just the start and end datetimes of each completed fast, in descending order
    return fasts[['start_dt', 'end_dt']]


def validate_discrete_fasts(fasts: pd.DataFrame, start_col: str = 'start_dt', end_col: str = 'end_dt') -> bool:
    """
    Validate a discrete log of fasts for use by other module functions.
    Discrete logs should have a start and end datetime for each fast.
    Validations:
        - Each fast has a start and end datetime (start_col and end_col cannot contain missing values)
        - Start datetimes are before end datetimes for each fast
        - Fasts do not overlap.

    Args:
        fasts: DataFrame of discrete logs with start and end datetime columns.
        start_col: Name of column representing fasting start datetimes.
        end_col: Name of column representing fasting end datetimes.

    Returns: True if the discrete fasts DataFrame is valid.
    """

    fasts = fasts.copy()
    fasts.sort_values(by=start_col, ascending=True, inplace=True, ignore_index=True)

    # TODO validate fasts[start_col] and fasts[end_col] data types

    # Validate no missing start or end datetimes
    start_end = fasts[[start_col, end_col]]
    if start_end.isnull().values.any():
        nan_rows = start_end.isnull().any(axis=1)
        nan_rows_indexes = nan_rows[nan_rows].index
        nan_fasts = fasts.iloc[nan_rows_indexes, :]
        raise ValueError(f"""
                        Discrete logs must contain start and end datetimes.
                        Check columns '{start_col}' and '{end_col}' for missing values:
                        {nan_fasts}
                        """)

    # validate start_dt < end_dt
    start_end_mismatch = fasts[start_col] > fasts[end_col]  # Is start datetime AFTER end datetime?
    if start_end_mismatch.any():  # If any mismatch
        conflicting_logs = fasts[start_end_mismatch]  # Subset fasts with start and end mismatch
        raise ValueError(f"""
                        Start datetime must be before associated end datetime.
                        The following fasts have start and end datetime conflicts:
                        {conflicting_logs}
                        """)

    # Validate no overlapping fasts
    intervals = pd.IntervalIndex.from_arrays(left=fasts.start_dt, right=fasts.end_dt.values)
    if intervals.is_overlapping:
        # get overlapping fasts
        previous_end_dt = fasts[end_col].shift(1).dropna()
        overlapping = previous_end_dt > fasts[start_col][1:]
        true_overlap = overlapping[overlapping]
        overlapping_fasts = fasts.iloc[true_overlap.index]
        raise ValueError(f"""
                        Overlapping fasts found in DataFrame.
                        The following fasts overlap with previous fast:
                        {overlapping_fasts}
                        """)

    return True


def validate_continuous_fasts(fasts: pd.Series) -> bool:
    """
    Validate a continuous log of fasts for use by other module functions.
    Validations:
        - Frequency of series index is 1 minute ('T')
        - Value at each time step is either 0 or 1 (0 ~ not fasting, 1 ~ fasting), no extraneous or NaN values

    Args:
        fasts: Series of continuous logs with a datetime index at a 1 minute frequency and values of 0 or 1.

    Returns: True if the fasts series is valid.
    """

    # Validate frequency of index is 1 minute ('T')
    freq = pd.infer_freq(fasts.index)
    if freq != 'T':
        raise ValueError(f"""
                        Frequency of the continuous fast must be: 'T' (1 minute).
                        Frequency of fasts series input: {freq}.
                        """)

    # Validate values only contain 0 or 1
    if not fasts.isin([0, 1]).all():
        unexpected_values = fasts[((fasts != 0) & (fasts != 1))]
        raise ValueError(f"""
                        Continuous fast (input to fasts) must contain only values of 0 or 1.
                        Check fasts for extraneous or NaN values:
                        {unexpected_values}
                        """)

    return True


def continuous_fasts(fasts: pd.DataFrame, start_col: str = 'start_dt', end_col: str = 'end_dt') -> pd.Series:
    """
    Create a continuous time series of fasting status (0 ~ no or 1 ~ yes)
    from a DataFrame of individual events (start datetime and end datetime)
    with a datetime index at a frequency of 1 minute.

    Args:
        fasts: DataFrame of discrete logs with start and end datetime columns.
        start_col: Name of column representing fasting start datetimes.
        end_col: Name of column representing fasting end datetimes.

    Returns: A pandas Series of event status at 1 minute frequency.
                - Yes (ie. fasting) as 1.
                - No (i.e. not fasting) as 0.

    """
    if not validate_discrete_fasts(fasts, 'start_dt', 'end_dt'):
        raise Exception('Discrete log is invalid. Check error raised by validate_discrete_log().')

    # Sort by start_dt (oldest to newest)
    fasts = fasts.sort_values(by=start_col, ascending=True, ignore_index=True)

    # Create continuous log
    start = fasts[start_col].iloc[0]  # First timestamp: start_dt of first fast
    end = fasts[end_col].iloc[-1]  # Last timestamp: end_dt of last fast
    time_range = pd.date_range(start=start, end=end, freq='1T')
    log = pd.Series(0, index=time_range)  # Initialize continuous log to 0
    for index, row in fasts.iterrows():  # Set fasting value to 1 for timestamps between fast start and end
        start = row[start_col]
        end = row[end_col]
        log[start:end] = 1

    return log


def daily_cumulative_hours(fasts: pd.Series) -> pd.Series:
    """
    Calculate the daily cumulative hours fasted from a pandas Series of fasting status with 1 minute frequency.
    Args:
        fasts: pandas Series of fasting status with 1 minute frequency.
                    - Yes (ie. fasting) as 1.
                    - No (i.e. not fasting) as 0.
    Returns: The daily cumulative hours fasted as a pandas Series.

    """
    if not validate_continuous_fasts(fasts):
        raise Exception('Continuous log is invalid. Check error raised by validate_continuous_log().')

    minutes_per_hour = 60
    cumulative_mins = fasts.resample('1D').sum()
    cumulative_hrs = cumulative_mins / minutes_per_hour
    return cumulative_hrs


def consecutive_minutes(fasts: pd.Series) -> pd.Series:
    """
    Create a time series of consecutive minutes (cumulative summation of each fast) fasted from
    a time series of fasting status.

    Example:
        Input =  [0,1,1,1,0,1,1]
        Output = [0,1,2,3,0,1,2]

    Args:
        fasts: pandas Series of fasting status with 1 minute frequency.
                    - Yes (ie. fasting) as 1.
                    - No (i.e. not fasting) as 0.
    Returns: A time series of a consecutive minutes fasted.

    Reference: Credit to George Pipis for inspiration of the solution.
               - Link:https://predictivehacks.com/count-the-consecutive-events-in-python/

    """

    if not validate_continuous_fasts(fasts):
        raise Exception('Continuous log is invalid. Check error raised by validate_continuous_log().')

    consecutive_mins = fasts.groupby((fasts != fasts.shift()).cumsum()).cumcount() + 1
    consecutive_mins[fasts == 0] = 0
    return consecutive_mins


def daily_max_consecutive_hours(fasts: pd.Series) -> pd.Series:
    """
    Calculate the maximum daily consecutive hours fasted from a pandas Series of fasting status with 1 minute frequency.

    There are potentially 2 fasts occurring in a single day (one ends and another starts).
    Maximum consecutive hours fasted his can include hours carried over from previous day.


    Args:
        fasts: pandas Series of fasting status with 1 minute frequency.
                    - Yes (ie. fasting) as 1.
                    - No (i.e. not fasting) as 0.
    Returns: The daily maximum consecutive hours fasted as a pandas Series.

    """

    if not validate_continuous_fasts(fasts):
        raise Exception('Continuous log is invalid. Check error raised by validate_continuous_log().')

    minutes_per_hour = 60
    consecutive_mins = consecutive_minutes(fasts)
    daily_maximum_mins = consecutive_mins.resample('1D').max()
    daily_maximum_hrs = daily_maximum_mins / minutes_per_hour
    return daily_maximum_hrs

# TODO fast_durations() -> calculate duration of each fast
# TODO fasting_zone() -> label each time step in a continuous log with the associated fasting zone
# TODO summary() -> input discrete log and get all stats back
# TODO add 'discrete:bool=False' parameter to most functions?
#  So users can go direct from discrete log to stats and csv to either discrete or continuous when loading log
