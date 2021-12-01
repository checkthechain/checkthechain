from ctc import directory
from ctc import evm
from ctc.protocols import chainlink_utils
from ctc.protocols import uniswap_v2_utils


#
# # pcv holdings
#


@evm.parallelize_block_fetching()
def fetch_pcv_uniswap_balance(block=None, **kwargs):
    address = directory.get_fei_address('EthUniswapPCVDeposit', block=block)
    lp_tokens = evm.get_erc20_balance_of(
        token=directory.uniswap_v2_pools['FEI_ETH'],
        address=address,
        block=block,
        **kwargs
    )
    return {'lp_tokens': lp_tokens}


@evm.parallelize_block_fetching()
def fetch_reserve_stabilizer_balance(block=None, **kwargs):
    address = directory.get_fei_address('EthReserveStabilizer', block=block)
    return evm.fetch_eth_balance(address, block=block, **kwargs)


@evm.parallelize_block_fetching()
def fetch_dripper_balance(block=None, **kwargs):
    address = directory.get_fei_address('EthPCVDripper', block=block)
    return evm.fetch_eth_balance(address, block=block, **kwargs)


@evm.parallelize_block_fetching()
def fetch_bonding_curve_balance(block=None, **kwargs):
    address = directory.get_fei_address('EthBondingCurve', block=block)
    return evm.fetch_eth_balance(address, block=block, **kwargs)


@evm.parallelize_block_fetching()
def fetch_pcv_steth_usd(block=None):
    pcv_steth = evm.get_erc20_balance_of(
        address=directory.get_fei_address('EthLidoPCVDeposit'),
        token='stETH',
        block=block,
    )
    # approximate using ETH price
    steth_price_usd = chainlink_utils.fetch_eth_price(block=block)
    return pcv_steth * steth_price_usd


@evm.parallelize_block_fetching()
def fetch_pcv_holdings(asset, block=None):

    # some values hardcoded for now, around block 13102065

    if block is not None:
        raise NotImplementedError()

    if asset == 'ETH':
        raise NotImplementedError()

    elif asset == 'stETH':
        return evm.get_erc20_balance_of(
            address=directory.get_fei_address('EthLidoPCVDeposit'),
            token='stETH',
            block=block,
        )

    elif asset == 'DPI':
        sushiswap_dpi = 24637
        rari_dpi = 2619
        return sushiswap_dpi + rari_dpi

    elif asset == 'DAI':
        return 50e6

    elif asset == 'RAI':
        return 795530.8634

    elif asset == 'INDEX':
        return 100000

    else:
        raise Exception('asset not recognized: ' + str(asset))


#
# # prices
#


@evm.parallelize_block_fetching()
def fetch_fei_price(block=None, **kwargs):
    kwargs.update({'block': block, 'format': 'answer'})
    kwargs.setdefault('normalize', True)
    usd_per_eth = chainlink_utils.fetch_feed_datum('ETH_USD', **kwargs)
    eth_per_fei = chainlink_utils.fetch_feed_datum('FEI_ETH', **kwargs)
    return usd_per_eth * eth_per_fei


@evm.parallelize_block_fetching()
def fetch_tribe_price(block=None, **kwargs):
    kwargs.update({'block': block, 'format': 'answer'})
    kwargs.setdefault('normalize', True)
    usd_per_eth = chainlink_utils.fetch_feed_datum('ETH_USD', **kwargs)
    eth_per_tribe = chainlink_utils.fetch_feed_datum('TRIBE_ETH', **kwargs)
    return usd_per_eth * eth_per_tribe


@evm.parallelize_block_fetching()
def fetch_rari_protocol_owned_fei(block=None):
    protocol_pool_tokens = evm.get_erc20_balance_of(
        address=directory.get_fei_address('Fei DAO Timelock'),
        token=directory.rari_pool_tokens['pool_8__FEI'],
        block=block,
    )
    total_pool_tokens = evm.get_erc20_total_supply(
        token=directory.rari_pool_tokens['pool_8__FEI'],
        block=block,
    )
    pool_fei = evm.get_erc20_balance_of(
        address=directory.rari_pool_tokens['pool_8__FEI'],
        token='FEI',
        block=block,
    )
    if total_pool_tokens == 0:
        return 0
    else:
        return protocol_pool_tokens / total_pool_tokens * pool_fei


@evm.parallelize_block_fetching(config={'to_dict_of_lists': True})
def fetch_fei_metrics(block=None):

    weth_address = directory.token_addresses['WETH']
    fei_address = directory.token_addresses['FEI']
    tribe_address = directory.token_addresses['TRIBE']

    # supply
    fei_total_supply = evm.get_erc20_total_supply(fei_address, block=block)
    tribe_total_supply = evm.get_erc20_total_supply(tribe_address, block=block)

    # oracle prices
    eth_price = chainlink_utils.fetch_eth_price(block=block)
    fei_price = None
    tribe_price = None

    # uni pool stats
    uni_v2__fei_eth = uniswap_v2_utils.fetch_uni_v2_pool_state(
        pool_address=directory.uniswap_v2_pools['FEI_ETH'],
        x_name='FEI',
        x_address=fei_address,
        x_price=fei_price,
        y_name='ETH',
        y_address=weth_address,
        y_price=eth_price,
        block=block,
    )
    uni_v2__fei_tribe = uniswap_v2_utils.fetch_uni_v2_pool_state(
        pool_address=directory.uniswap_v2_pools['FEI_TRIBE'],
        x_name='FEI',
        x_address=fei_address,
        x_price=fei_price,
        y_name='TRIBE',
        y_address=tribe_address,
        y_price=tribe_price,
        block=block,
    )

    # pcv
    reserve_stabilizer_balance = fetch_reserve_stabilizer_balance(block=block)
    dripper_balance = fetch_dripper_balance(block=block)
    bonding_curve_balance = fetch_bonding_curve_balance(block=block)
    pcv_uniswap_balance = fetch_pcv_uniswap_balance(block=block)
    pcv_fei_eth_lp_fraction = (
        pcv_uniswap_balance['lp_tokens'] / uni_v2__fei_eth['lp_tokens']
    )
    pcv_uniswap_usd = pcv_fei_eth_lp_fraction * uni_v2__fei_eth['ETH_tvl']
    pcv_dripper_usd = eth_price * (
        reserve_stabilizer_balance + dripper_balance + bonding_curve_balance
    )
    pcv_steth_usd = fetch_pcv_steth_usd(block=block)
    pcv_total_usd = pcv_uniswap_usd + pcv_dripper_usd + pcv_steth_usd

    # types of fei
    rari_protocol_owned_fei = fetch_rari_protocol_owned_fei(block=block)
    uniswap_protocol_owned_fei = (
        pcv_fei_eth_lp_fraction * uni_v2__fei_eth['FEI_balance']
    )
    protocol_owned_fei = rari_protocol_owned_fei + uniswap_protocol_owned_fei
    user_owned_fei = fei_total_supply - protocol_owned_fei
    collateralization_ratio = pcv_total_usd / user_owned_fei

    return {
        # total supply
        'FEI_TOTAL_SUPPLY': fei_total_supply,
        'TRIBE_TOTAL_SUPPLY': tribe_total_supply,
        # oracle prices
        'ETH_PRICE': eth_price,
        # uniswap pools
        'UNI_V2_FEI_ETH': uni_v2__fei_eth,
        'UNI_V2_FEI_TRIBE': uni_v2__fei_tribe,
        # pcv
        'PCV_UNISWAP_USD': pcv_uniswap_usd,
        'PCV_TOTAL_USD': pcv_total_usd,
        # types of FEI
        'PROTOCOL_OWNED_FEI': protocol_owned_fei,
        'USER_OWNED_FEI': user_owned_fei,
        'COLLATERALIZATION_RATIO': collateralization_ratio,
    }

