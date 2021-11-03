import numpy as np
import pandas as pd

from ctc import directory
from ctc import evm
from ctc.toolbox import web3_utils


#
# # addresses
#

co_addresses = {
    'StaticPCVDepositWrapper': '0x8B41DcEfAe6064E6bc2A9B3ae20141d23EFD6cbd',
    'CollateralizationOracle': '0xFF6f59333cfD8f4Ebc14aD0a0E181a83e655d257',
    'CollateralizationOracleWrapper_TransparentUpgradeableProxy': '0xd1866289B4Bd22D453fFF676760961e0898EE9BF',
    'CollateralizationOracleWrapper_ProxyImplementation': '0x656aA9c9875eB089b11869d4730d6963D25E76ad',
    'ProxyAdmin': '0xf8c2b645988b7658e7748ba637fe25bdd46a704a',
}
co_addresses = {k: v.lower() for k, v in co_addresses.items()}


def _get_co_address(wrapper):
    if wrapper:
        return co_addresses[
            'CollateralizationOracleWrapper_TransparentUpgradeableProxy'
        ]
    else:
        return co_addresses['CollateralizationOracle']


#
# # summary
#


def get_pcv_stats(block=None, blocks=None, wrapper=False):

    # assemble kwargs
    kwargs = {}
    if wrapper:
        kwargs['contract'] = co_addresses[
            'CollateralizationOracleWrapper_TransparentUpgradeableProxy'
        ]
    else:
        kwargs['contract'] = co_addresses['CollateralizationOracle']
    if block is not None:
        kwargs['block'] = block
    if blocks is not None:
        kwargs['blocks'] = blocks

    # fetch results
    result = web3_utils.call_web3_contract(function='pcvStats', **kwargs)

    # arrange results
    keys = ['pcv', 'user_fei', 'protocol_equity', 'valid']
    transpose = list(zip(*result))
    data = {}
    for k, key in enumerate(keys):
        data[key] = transpose[k]
        data[key] = np.array(data[key])
        if key in ['pcv', 'user_fei', 'protocol_equity']:
            data[key] = data[key] / 1e18

    # create dataframe
    df = pd.DataFrame(data, index=blocks)

    return df


#
# # deposits
#


def get_deposits_for_token(token, block=None, wrapper=False):

    # assemble kwargs
    kwargs = {}
    if wrapper:
        kwargs['contract'] = co_addresses[
            'CollateralizationOracleWrapper_TransparentUpgradeableProxy'
        ]
    else:
        kwargs['contract'] = co_addresses['CollateralizationOracle']

    token = evm.get_address_checksum(token)

    result = web3_utils.call_web3_contract(
        function='getDepositsForToken',
        kwargs={'_token': token},
        block=block,
        **kwargs
    )

    return [item.lower() for item in result]


def get_tokens_deposits():
    tokens_deposits = {}
    for token in get_tokens_in_pcv():
        tokens_deposits[token] = get_deposits_for_token(token)
    return tokens_deposits


def get_deposit_token_balance(deposit_address, block=None):

    deposit_address = evm.get_address_checksum(deposit_address)

    balance = web3_utils.call_web3_contract(
        contract=deposit_address,
        function='balance',
        block=block,
    )
    return balance


#
# # specific tokens
#


def get_tokens_in_pcv(block=None, wrapper=False):
    tokens = web3_utils.call_web3_contract(
        contract=_get_co_address(wrapper=wrapper),
        function='getTokensInPcv',
        block=block,
    )
    return [token.lower() for token in tokens]


def get_pcv_token_balance(token, block=None):

    # assemble kwargs
    kwargs = {}
    kwargs['contract'] = co_addresses['CollateralizationOracle']

    deposits = get_deposits_for_token(token=token, block=block)
    pcv_token_balance = 0
    for deposit in deposits:
        pcv_token_balance += get_deposit_token_balance(
            deposit_address=deposit, block=block
        )

    return pcv_token_balance


def get_token_price_usd(token, block=None):

    if token.lower() == '0x03ab458634910aad20ef5f1c8ee96f1d6ac54919':
        # RAI composite oracle
        # RAI-ETH oracle
        rai_eth_oracle = directory.chainlink_feeds['RAI_ETH']
        rai_eth = web3_utils.call_web3_contract(
            contract=rai_eth_oracle, function='latestAnswer'
        )
        rai_eth /= 1e18

        # ETH-USD oracle
        eth_usd_oracle = directory.chainlink_feeds['ETH_USD']
        eth_usd = web3_utils.call_web3_contract(
            contract=eth_usd_oracle, function='latestAnswer'
        )
        eth_usd /= 1e8

        rai_usd = rai_eth * eth_usd

        return rai_usd

    elif token.lower() == '0x956f47f50a910163d8bf957cf5846d573e7f87ca':

        # FEI
        # constant oracle
        return 1

    else:
        oracle = token_to_oracle(token)
        oracle = evm.get_address_checksum(oracle)

        chainlink_oracle = web3_utils.call_web3_contract(
            contract=oracle, function='chainlinkOracle'
        )

        chainlink_oracle = evm.get_address_checksum(chainlink_oracle)
        answer = web3_utils.call_web3_contract(
            contract=chainlink_oracle, function='latestAnswer'
        )

        return answer / 1e8


def get_pcv_token_balance_usd(token, block=None):
    token_balance = get_pcv_token_balance(token, block=None, wrapper=False)
    token_price_usd = get_token_price_usd(token=token, block=block)
    return token_balance * token_price_usd


def token_to_oracle(token_address, block=None):
    address = evm.get_address_checksum(co_addresses['CollateralizationOracle'])
    return web3_utils.call_web3_contract(
        contract=address,
        function='tokenToOracle',
        args=[evm.get_address_checksum(token_address)],
        block=block,
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
    df = pd.DataFrame(rows)
    return df
