import pytest

from ctc.toolbox.defi_utils import dex_utils


#
# # test get dex pools
#

example_pool_queries = [
    {
        'query': {
            'assets': ['0x5f98805a4e8be255a32880fdec7f6728c6568ba0'],
        },
        'results': [
            '0xb0f75e97a114a4eb4a425edc48990e6760726709',
            '0xede4efcc5492cf41ed3f0109d60bc0543cfad23a',
            '0x5a172919fff040196b36b238b9e2e7e6d33f616a',
            '0xc4451498f950b8b3abd9a815cf221a8e64791388',
            '0x1b46e4b0791c9383b73b64aabc371360a031a83f',
            '0xb39362c3d5ac235fe588b0b83ed7ac87241039cb',
            '0xd652c40fbb3f06d6b58cb9aa9cff063ee63d465d',
            '0xed279fdd11ca84beef15af5d39bb4d4bee23f0ca',
            '0x497ce58f34605b9944e6b15ecafe6b001206fd25',
            '0xa0d35faead5299bf18efbb5defd1ec6d4ab4ef3b',
            '0x780d605cd56043664478292705bf8027f215942f',
            '0x46e4d8a1322b9448905225e52f914094dbd6dddf',
            '0x279ca79d5fb2490721512c8ae4767e249d75f41b',
            '0xfdf12d1f85b5082877a6e070524f50f6c84faa6b',
            '0x20062da66f4d36942313c3395e5936cf04e8320a',
            '0xf20ef17b889b437c151eb5ba15a47bfc62bff469',
            '0x477a61f69d468fb61224a33b7b0d4de647b4f704',
            '0x6255550a53fd12b7131c0829dc439c5e02eebca8',
            '0x16980c16811bde2b3358c1ce4341541a4c772ec9',
            '0xbcc2adccd4de0b2656179f729c98c39dcd68c84d',
            '0xa31a285832edbffef40d271a4ff1180bdd30237f',
            '0xf1ddc084500fc774bb835f412aea908259b55ce4',
            '0xd251dff33e31bb98d5587e5b1004ff01a5a41289',
            '0xaaadbb0d64f6d25731306f11e9ee94b486d53e43',
            '0x159109cacaf431005099b73ef8b66069682a66b4',
            '0x4e0924d3a751be199c426d52fb1f2337fa96f736',
            '0x9902affdd3b8ef60304958c60377110c6d6ab1df',
            '0x67e887913b13e280538c169f13d169a659a203de',
            '0x5c09448abfdcb638ea992ce3e45bbc1d7ec7c4cf',
            '0x9663f2ca0454accad3e094448ea6f77443880454',
            '0x2746f8ee2390b33e87c39d9f786b6a004f212064',
            '0x54a0f2d8bd71b793d008266005dfae136500b204',
            '0xd4cd70c4569f1e3661d50004449fd501a386237c',
            '0x2020b31a89fb359ffcb2933f4bba65da6f27d0fe',
            '0xb065c77afc6e1a03b6166ac0fb2f4e84ff6a24d4',
        ],
    },
]


@pytest.mark.parametrize('test', example_pool_queries)
async def test_get_pools(test):
    pools = await dex_utils.async_get_pools(**test['query'])
    assert set(pool['address'] for pool in pools) == set(test['results'])


#
# # test getting DEX balances
#

example_balances = [
    # balancer pool
    {
        'query': {
            'block': 14000000,
            'pool': 'address',
        },
        'result': {
            'token0': 0,
            'token1': 0,
        },
    },
    # curve pool
    {
        'query': {
            'block': 14000000,
            'pool': 'address',
        },
        'result': {
            'token0': 0,
            'token1': 0,
        },
    },
    # uniswap v2 pool
    {
        'query': {
            'block': 14000000,
            'pool': 'address',
        },
        'result': {
            'token0': 0,
            'token1': 0,
        },
    },
    # uniswap v3 pool
    {
        'query': {
            'block': 14000000,
            'pool': 'address',
        },
        'result': {
            'token0': 0,
            'token1': 0,
        },
    },
]


@pytest.mark.parametrize('test', example_balances)
async def test_get_pool_balances(test):
    pool_balances = await dex_utils.async_get_pool_balances(**test['query'])
    assert set(pool_balances.keys()) == set(test['result'])
    for key in pool_balances.keys():
        pool_balances[key] == test['result'][key]


#
# # test getting dex swaps
#

example_swap_queries = [
    {
        'query': {
            'pool': 'address',
            'start_block': 0,
            'end_block': 0,
        },
        'results': {
            'n_swaps': 0,
        },
    },
]


@pytest.mark.parametrize('test', example_swap_queries)
async def test_get_pool_swaps(test):
    swaps = await dex_utils.async_get_pool_swaps(**test['query'])
    assert swaps['results']['n_swaps'] == len(swaps)
