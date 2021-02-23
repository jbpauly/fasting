#!/usr/bin/env python

"""Tests for `fasting` package."""

import pytest
from fasting import quantify
import pandas as pd

FAST_STARTS = ['1/16/21 20:05:00', '1/17/21 12:15:00']
FAST_ENDS = ['1/17/21 10:05:00', '1/18/21 12:15:00']
ZERO_FAST_DATA_EXPORT = [['2/12/21', '9:55', '0'],
                         ['1/17/21', '12:15', '12:15', '24', '1'],
                         ['1/16/21', '20:05', '10:05', '14', '2']]


@pytest.fixture(scope='session')
def zero_log(tmpdir_factory):
    dataframe = pd.DataFrame(ZERO_FAST_DATA_EXPORT,
                             columns=['Date', 'Start', 'End', 'Hours', 'Night Eating']
                             )
    filename = str(tmpdir_factory.mktemp('data').join('data.csv'))
    dataframe.to_csv(filename)
    return filename


@pytest.fixture(scope='session')
def zero_log_false(tmpdir_factory):
    dataframe = pd.DataFrame(ZERO_FAST_DATA_EXPORT,
                             columns=['Date', 'Start', 'End', 'hrs', 'Night Eating']
                             )
    filename = str(tmpdir_factory.mktemp('data').join('data.csv'))
    dataframe.to_csv(filename)
    return filename


@pytest.fixture(scope='session')
def discrete():
    discrete_log = {'start_dt': FAST_STARTS,
                    'end_dt': FAST_ENDS}
    discrete_data = pd.DataFrame(data=discrete_log, dtype='datetime64[ns]')
    return discrete_data


@pytest.fixture(scope='session')
def continuous():
    datetime_range = pd.date_range(start=FAST_STARTS[0], end=FAST_ENDS[1], freq='1T')
    continuous_data = pd.Series(0, index=datetime_range)
    continuous_data[FAST_STARTS[0]: FAST_ENDS[0]] = 1
    continuous_data[FAST_STARTS[1]: FAST_ENDS[1]] = 1
    return continuous_data


@pytest.fixture(scope='session')
def continuous_short():
    datetime_range = pd.date_range(start='1/1/21 23:56:00', end='1/2/21 00:02:00', freq='1T')
    # Fasting Key: {not fasting: 0, fasting: 1}

    fasting = [1,  # '1/1/21 23:56:00'
               0,  # '1/1/21 23:57:00'
               1,  # '1/1/21 23:58:00'
               1,  # '1/1/21 23:59:00'
               1,  # '1/2/21 00:00:00'
               1,  # '1/2/21 00:01:00'
               1]  # '1/2/21 00:02:00'

    continuous_data = pd.Series(data=fasting, index=datetime_range)
    return continuous_data


@pytest.fixture(scope='session')
def continuous_short_consecutive():
    datetime_range = pd.date_range(start='1/1/21 23:56:00', end='1/2/21 00:02:00', freq='1T')
    # Fasting Key: {not fasting: 0, fasting: 1}
    # fasting = [1,  # '1/1/21 23:56:00'
    #            0,  # '1/1/21 23:57:00'
    #            1,  # '1/1/21 23:58:00'
    #            1,  # '1/1/21 23:59:00'
    #            1,  # '1/2/21 00:00:00'
    #            1,  # '1/2/21 00:01:00'
    #            1]  # '1/2/21 00:02:00'

    # fasting =     [1, 0, 1, 1, 1, 1, 1]
    # consecutive = [1, 0, 1, 2, 3, 4, 5]

    consecutive = [1,  # '1/1/21 23:56:00'
                   0,  # '1/1/21 23:57:00'
                   1,  # '1/1/21 23:58:00'
                   2,  # '1/1/21 23:59:00'
                   3,  # '1/2/21 00:00:00'
                   4,  # '1/2/21 00:01:00'
                   5]  # '1/2/21 00:02:00'

    continuous_data = pd.Series(data=consecutive, index=datetime_range)
    return continuous_data


def test_load_zero(zero_log, zero_log_false, discrete):
    # Positive test
    output = quantify.zero_fasts(zero_log)
    assert output.equals(discrete)

    # Negative test: CSV file with unexpected column
    with pytest.raises(ValueError):
        assert quantify.zero_fasts(zero_log_false)


def test_validate_discrete_fasts(discrete):
    # Positive test
    assert quantify.validate_discrete_fasts(fasts=discrete, start_col='start_dt', end_col='end_dt')

    # Negative test

    # Missing start or end datetime
    missing_start = discrete.copy()
    missing_start['start_dt'] = None
    missing_end = discrete.copy()
    missing_end['end_dt'] = None
    with pytest.raises(ValueError):
        assert quantify.validate_discrete_fasts(fasts=missing_start, start_col='start_dt', end_col='end_dt')
    with pytest.raises(ValueError):
        assert quantify.validate_discrete_fasts(fasts=missing_end, start_col='start_dt', end_col='end_dt')

    # Mismatch in start and end datetime
    #   - start datetime is AFTER end datetime
    with pytest.raises(ValueError):
        # swap start_col and end_col
        assert quantify.validate_discrete_fasts(fasts=discrete, start_col='end_dt', end_col='start_dt')

    # Overlapping fasts
    #   - Swap: end datetime of fast 00,  start datetime of fast 01
    overlapping = discrete.copy()
    overlapping.at[0, 'end_dt'] = discrete.at[1, 'start_dt']
    overlapping.at[1, 'start_dt'] = discrete.at[0, 'end_dt']
    with pytest.raises(ValueError):
        assert quantify.validate_discrete_fasts(fasts=overlapping, start_col='start_dt', end_col='end_dt')


def test_continuous_fasts(discrete, continuous, mocker):
    mocker.patch.object(quantify, "validate_discrete_fasts", return_value=True)  # assume dataset is valid

    # Positive test
    output = quantify.continuous_fasts(fasts=discrete)
    assert output.equals(continuous)


def test_validate_continuous_fasts(continuous):
    # Positive test
    assert quantify.validate_continuous_fasts(continuous)

    # Negative test

    # Unexpected frequency of datetimeindex
    # Expected frequency is 1 minute ('T')
    wrong_frequency = continuous.resample('1D').max()
    with pytest.raises(ValueError):
        assert quantify.validate_continuous_fasts(wrong_frequency)

    # Unexpected frequency of data points
    # Expected values [0,1]

    wrong_values = continuous.copy()
    wrong_values[:] = 2
    null_values = continuous.copy()
    null_values[:] = None

    with pytest.raises(ValueError):
        assert quantify.validate_continuous_fasts(wrong_values)
    with pytest.raises(ValueError):
        assert quantify.validate_continuous_fasts(null_values)


def test_daily_cumulative_hours(continuous_short, mocker):
    # fasting = [1,  # '1/1/21 23:56:00'
    #            0,  # '1/1/21 23:57:00'
    #            1,  # '1/1/21 23:58:00'
    #            1,  # '1/1/21 23:59:00'
    #            1,  # '1/2/21 00:00:00'
    #            1,  # '1/2/21 00:01:00'
    #            1]  # '1/2/21 00:02:00'

    mocker.patch.object(quantify, "validate_continuous_fasts", return_value=True)  # assume dataset is valid

    dates = ['1/1/21', '1/2/21']
    dates_index = pd.date_range(start=dates[0], end=dates[1], freq='1D')
    minutes_per_hour = 60.0
    minutes_fasted = 3.0
    hours_fasted = minutes_fasted / minutes_per_hour
    daily_hours_fasted = [hours_fasted, hours_fasted]
    expected_output = pd.Series(data=daily_hours_fasted, index=dates_index)

    # Positive test
    output = quantify.daily_cumulative_hours(fasts=continuous_short)
    assert output.equals(expected_output)


def test_consecutive_minutes(continuous_short, continuous_short_consecutive, mocker):

    mocker.patch.object(quantify, "validate_continuous_fasts", return_value=True)  # assume dataset is valid

    expected_output = continuous_short_consecutive
    # Positive test
    output = quantify.consecutive_minutes(fasts=continuous_short)
    assert output.equals(expected_output)


def test_daily_max_consecutive_hours(continuous_short, continuous_short_consecutive, mocker):

    mocker.patch.object(quantify, "validate_continuous_fasts", return_value=True)  # assume dataset is valid
    mocker.patch.object(quantify, "consecutive_minutes", return_value=continuous_short_consecutive)

    minutes_per_hour = 60
    expected_maximum_minutes = [2, 5]
    expected_maximum_hours = [value / minutes_per_hour for value in expected_maximum_minutes]

    # Positive test
    output = quantify.daily_max_consecutive_hours(continuous_short)
    assert list(output) == expected_maximum_hours
