import pandas as pd

from ctc import evm
from ctc import directory
from ctc.toolbox import etl_utils


def load_fei_transactions(**load_kwargs):
    return load_fei_etl('transactions', **load_kwargs)


def load_fei_token_transfers(**load_kwargs):
    return load_fei_etl('token_transfers', **load_kwargs)


def load_fei_logs(**load_kwargs):
    return load_fei_etl('logs', **load_kwargs)


def load_fei_etl(
    rowtype, block_timestamps=None, format_values=True, **load_kwargs
):
    """load_kwargs includes `columns` and `etl_view`

    should really move all of this functionality into etl.load_data()
    """

    export_list = etl_utils.list_exported_data(
        rowtype, etl_view='fei_ecosystem', **load_kwargs
    )

    df = etl_utils.load_data(
        rowtype,
        etl_view='fei_ecosystem',
        start_block=export_list['start_block'],
        end_block=export_list['end_block'],
        **load_kwargs
    )

    if format_values:
        etl_utils.format_raw_dataframe(
            df, convert_to_type='decimal', rescale_factor=1e18,
        )
        if rowtype == 'logs':
            df = etl_utils.format_log_dataframe(df)

    if block_timestamps is not None:
        timestamps = pd.Series(block_timestamps)[df['block_number']].values
        df['block_timestamp'] = timestamps
        df['block_datetime'] = pd.to_datetime(timestamps, unit='s')

    return df


def get_reweight_data():
    """return dataframe of reweight events

    ## Columns
    - block
    - timestamp
    - uni_tvl_before
    - uni_fei_before
    - uni_eth_before
    - uni_tvl_after
    - uni_fei_before
    - uni_eth_after
    - fei_purchased
    - eth_sold
    """
    pass


def get_bonding_curve_data(token, logs=None, include_genesis=False):
    """return dataframe of bonding curve issuance events"""

    # load logs
    if logs is None:
        logs = load_fei_logs()

    # get contract
    if token == 'ETH':
        contract_name = 'EthBondingCurve'
    elif token == 'DPI':
        contract_name = 'DPIBondingCurve'
    else:
        raise Exception('unknown bonding curve: ' + str(token))

    # filter events
    df = evm.filter_events(
        event_name='Purchase',
        contract_name=contract_name,
        protocol='fei',
        raw_events=logs,
        contract_address=directory.get_fei_address(contract_name),
    )

    # exclude genesis purchase
    if token == 'ETH' and not include_genesis:
        df = df.iloc[1:]

    return df


def get_fei_uniswap_trade_data():
    """return dataframe of uniswap trades"""
    pass


def get_fei_uniswap_liquidity_data():
    """return dataframe of uniswap liquidity events"""
    pass

