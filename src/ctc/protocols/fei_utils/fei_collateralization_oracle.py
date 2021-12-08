import asyncio

from ctc import directory
from ctc import evm
from ctc import rpc
from ctc.evm import rpc_utils
from ctc.protocols import chainlink_utils


def get_token_price_usd(token, block=None):

    if token.lower() == '0x03ab458634910aad20ef5f1c8ee96f1d6ac54919':
        # RAI composite oracle
        # RAI-ETH oracle
        rai_eth_oracle = directory.chainlink_feeds['RAI_ETH']
        rai_eth = chainlink_utils.fetch_feed_value(
            feed=rai_eth_oracle, block=block
        )

        # ETH-USD oracle
        eth_usd_oracle = directory.chainlink_feeds['ETH_USD']
        eth_usd = chainlink_utils.fetch_feed_value(
            feed=eth_usd_oracle,
            block=block,
        )

        rai_usd = rai_eth * eth_usd

        return rai_usd

    elif token.lower() == '0x956f47f50a910163d8bf957cf5846d573e7f87ca':

        # FEI
        # constant oracle
        return 1

    else:
        oracle = token_to_oracle(token)
        oracle = evm.get_address_checksum(oracle)

        chainink_oracle = rpc_utils.eth_call(
            to_address=oracle,
            function_name='chainlinkOracle',
        )

        chainlink_oracle = evm.get_address_checksum(chainlink_oracle)
        answer = rpc_utils.eth_call(
            to_address=chainlink_oracle,
            function='latestAnswer',
        )

        return answer / 1e8


def get_pcv_token_balance_usd(token, block=None):
    token_balance = get_pcv_token_balance(token, block=None, wrapper=False)
    token_price_usd = get_token_price_usd(token=token, block=block)
    return token_balance * token_price_usd


def token_to_oracle(token_address, block=None):
    return rpc_utils.eth_call(
        to_address=co_addresses['CollateralizationOracle'],
        function_name='tokenToOracle',
        function_parameters=[token_address],
        block_number=block,
    )


def get_tokens_deposits_balances(tokens_deposits):
    skip_deposits = '0x7eb88140af813294aedce981b6ac08fcd139d408'
    tokens_balances = {}
    for token, token_deposits in tokens_deposits.items():
        tokens_balances[token] = {}
        for token_deposit in token_deposits:
            if token_deposit in skip_deposits:
                print('skipping', token_deposit)
                tokens_balances[token][token_deposit] = None
            else:
                tokens_balances[token][
                    token_deposit
                ] = get_deposit_token_balance(deposit_address=token_deposit)
                tokens_balances[token][token_deposit] /= 1e18
    return tokens_balances


def get_tokens_prices(tokens_deposits):
    skip_tokens = ['0x1111111111111111111111111111111111111111']
    token_prices_usd = {}
    for token in tokens_deposits.keys():
        if token in skip_tokens:
            print('skipping', token)
            token_prices_usd[token] = None
        else:
            token_prices_usd[token] = get_token_price_usd(token)
    return token_prices_usd


def get_deposits_dataframe(token_prices_usd=None, tokens_balances=None):
    if token_prices_usd is None:
        token_prices_usd = get_tokens_prices()
    if tokens_balances is None:
        tokens_blaances = get_tokens_deposits_balances()

    rows = []
    for token in tokens_in_pcv:
        if token == '0x1111111111111111111111111111111111111111':
            token_name = 'black_hole'
        else:
            token_name = directory.address_to_symbol.get(token, token)
        for deposit in tokens_deposits[token]:
            token_balance = token_balances[token][deposit]
            token_price = token_prices_usd[token]
            if token_balance is not None and token_price is not None:
                usd_balance = token_balance * token_price
            else:
                usd_balance = None

            row = {
                'token_name': token_name,
                'deposit': deposit,
                'token_balance': token_balance,
                'token_price': token_price,
                'usd_balance': usd_balance,
                'token_address': token,
            }
            rows.append(row)

    import pandas as pd

    df = pd.DataFrame(rows)
    return df

