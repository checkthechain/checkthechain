from ctc.protocols import uniswap_utils


def test_fetch_uni_v2_pool_state():
    results = uniswap_utils.fetch_uni_v2_pool_state(
        pool_address='0x94B0A3d511b6EcDb17eBF877278Ab030acb0A878',
        x_address='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
        y_address='0x956F47F50A910163D8BF957Cf5846D573E7f87CA',
        block=13437866,
        x_name='WETH',
        y_name='FEI',
        normalize=False,
    )
    assert results['WETH_balance'] == 36632373146254861687157
    assert results['FEI_balance'] == 136219847556588434237761989
    assert results['lp_tokens'] == 2152734217700018553905574

