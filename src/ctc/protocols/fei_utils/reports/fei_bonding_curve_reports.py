"""functions apply to data loaded with fei_data.get_bonding_curve_data"""

import matplotlib.pyplot as plt
import numpy as np

import toolplot

from ctc.toolbox import etl_utils


def plot_bonding_curve_summary(df, block_timestamps=None, token_name=None):

    if block_timestamps is None:
        block_timestamps = etl_utils.load_block_timestamps()

    plot_bonding_curve_size_distribution(df, token_name=token_name)
    plt.show()
    plot_bonding_curve_purchases_over_time(df, token_name=token_name)
    plt.show()
    plot_bonding_curve_cummulative_total(df, token_name=token_name)
    plt.show()
    plot_bonding_curve_by_day(
        df=df, block_timestamps=block_timestamps, token_name=token_name
    )
    plt.show()
    plot_bonding_curve_by_week(
        df=df, block_timestamps=block_timestamps, token_name=token_name
    )
    plt.show()


def plot_bonding_curve_size_distribution(df, token_name=None):
    ai = _get_amount_in_series(df)
    float_values = np.array(ai.values).astype(float)
    plt.hist(float_values / 1e18, 15, color='g')
    plt.yscale('log')
    plt.xlabel(token_name + ' amount in')
    plt.ylabel('number of purchases')
    if token_name is None:
        token_name = ' '
    else:
        token_name = ' ' + token_name + ' '
    plt.title('Distribution of' + token_name + 'bonding curve purchase sizes')


def plot_bonding_curve_purchases_over_time(df, token_name=None):
    ai = _get_amount_in_series(df)
    plt.plot(ai / 1e18, 'xg', alpha=0.5)
    toolplot.format_xticks_as_blocks()
    if token_name is None:
        token_name = 'Token'
    plt.ylabel(token_name + ' in')
    plt.xlabel('blocks')
    plt.title(token_name + ' Bonding Curve Purchases Over Time')


def plot_bonding_curve_cummulative_total(df, token_name=None):
    ai = _get_amount_in_series(df)
    plt.plot(np.cumsum(ai) / 1e18, 'g')
    toolplot.format_xticks_as_blocks()
    toolplot.format_yticks_as_numbers()
    if token_name is None:
        token_name = 'token',
    plt.ylabel('cummulative ' + token_name)
    plt.title('Total cummulative ' + token_name + ' input in bonding curve')


def _get_amount_in_series(df):
    if '_amountIn' in df.columns:
        ai = df['_amountIn']
    elif 'amountIn' in df.columns:
        ai = df['amountIn']
    else:
        raise Exception('could not find amountIn')

    if 'transaction_index' in ai.index.names:
        ai = ai.droplevel('transaction_index')
    if 'log_index' in ai.index.names:
        ai = ai.droplevel('log_index')

    return ai


def plot_bonding_curve_by_day(df, block_timestamps=None, token_name=None):
    f = df.copy()

    kwargs = {'block_timestamps': block_timestamps}
    f['datetime'] = etl_utils.create_block_datetime_column(f, **kwargs)
    f['date'] = etl_utils.create_block_date_column(f, **kwargs)

    if 'amountIn' in f:
        f['amountIn'] = f['amountIn'].astype(float)
    elif '_amountIn' in f:
        f['_amountIn'] = f['_amountIn'].astype(float)
    amount_in_series = _get_amount_in_series(f.groupby('date').sum())

    bonding_curve_by_day = etl_utils.add_missing_series_dates(
        amount_in_series,
        f['datetime'],
    )

    plt.plot(bonding_curve_by_day / 1e18, '.-g', markersize=10)
    toolplot.format_yticks_as_numbers()
    plt.xticks(rotation=-90)
    plt.xlabel('day')
    if token_name is None:
        token_name = 'token'
    plt.ylabel(token_name + ' in')
    plt.title(token_name + ' bonding curve input per day')


def plot_bonding_curve_by_week(df, block_timestamps=None, token_name=None):

    f = df.copy()

    kwargs = {'block_timestamps': block_timestamps}
    f['datetime'] = etl_utils.create_block_datetime_column(f, **kwargs)
    f['week'] = etl_utils.create_block_week_column(f, **kwargs)

    if 'amountIn' in f:
        f['amountIn'] = f['amountIn'].astype(float)
    elif '_amountIn' in f:
        f['_amountIn'] = f['_amountIn'].astype(float)
    amount_in_series = _get_amount_in_series(f.groupby('week').sum())

    bonding_curve_by_week = etl_utils.add_missing_series_weeks(
        amount_in_series,
        f['datetime'],
    )

    plt.plot(bonding_curve_by_week / 1e18, '.-g', markersize=10)
    toolplot.format_yticks_as_numbers()
    plt.xticks(rotation=-90)
    plt.xlabel('week')
    if token_name is None:
        token_name = 'token'
    plt.ylabel(token_name + ' in')
    plt.title(token_name + ' bonding curve input per week')

