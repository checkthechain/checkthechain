from ctc import evm
from . import rari_directory
from . import sushi_directory
from . import uniswap_directory


null_address = '0x0000000000000000000000000000000000000000'


token_addresses = {
    'WETH': '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
    'stETH': '0xae7ab96520de3a18e5e111b5eaab095312d7fe84',
    # FEI
    'FEI': '0x956f47f50a910163d8bf957cf5846d573e7f87ca',
    'TRIBE': '0xc7283b66eb1eb5fb86327f08e1b5816b0720212b',
    'FGEN': '0xbffb152b9392e38cddc275d818a3db7fe364596b',
    # stablecoins
    'USDT': '0xdac17f958d2ee523a2206206994597c13d831ec7',
    'USDC': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
    'BUSD': '0x4fabb145d64652a948d72533023f6e7a623c7c53',
    'DAI': '0x6b175474e89094c44da98b954eedeac495271d0f',
    'UST': '0xa47c8bf37f92abed4a126bda807a7b7498661acd',
    'PAX': '0x8e870d67f660d95d5be530380d0ec0bd388289e1',
    'HUSD': '0xdf574c24545e5ffecb9a659c229253d4111d87e1',
    'TUSD': '0x0000000000085d4780b73119b644ae5ecd22b376',
    'SUSD': '0x57ab1ec28d129707052df4df418d58a2d46d5f51',
    'USDN': '0x674c6ad92fd080e4004b2312b45f796a192d27a0',
    'GUSD': '0x056fd409e1d7a124bd7017459dfea2f387b6d5cd',
    'FRAX': '0x853d955acef822db058eb8505911ed77f175b99e',
    'USDP': '0x1456688345527be1f37e9e627da0837d6f08c925',
    'ESD': '0x36f3fd68e7325a35eb768f1aedaae9ea0689d723',
    'WBTC': '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
    'ALUSD': '0xbc6da0fe9ad5f3b0d58160288917aa56653660e9',
    # other
    'CHI': '0x0000000000004946c0e9f43f4dee607b0ef1fa1c',
    'AAVE': '0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9',
    'O3': '0xee9801669c6138e84bd50deb500827b776777d28',
    '3CRV': '0x6c3f90f043a72fa612cbac8115ee7e52bde6e490',
    'FXS': '0x3432b6a60d23ca0dfca7761b7ab56459d9c964d0',
    'ZKS': '0xe4815ae53b124e7263f08dcdbbb757d41ed658c6',
    'BRIBE': '0x679fa6dc913acab6def33ec469fc6e421bc794f5',
    'LUSD': '0x5f98805a4e8be255a32880fdec7f6728c6568ba0',
    'MKR': '0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2',
    'AUDIO': '0x18aaa7115705e8be94bffebde57af9bfc265b998',
    'DODO': '0x43dfc4159d86f3a37a5a4b3d4580b888ad7d4ddd',
}

# add uniswap tokens
for _pair, _address in uniswap_directory.uniswap_v2_pools.items():
    token_addresses['univ2_' + _pair] = _address
for _pair, _address in uniswap_directory.uniswap_v3_pools.items():
    token_addresses['univ3_' + _pair] = _address
for _pair, _address in sushi_directory.sushi_pools.items():
    token_addresses['sushi_' + _pair] = _address

address_to_symbol = evm.create_reverse_address_map(token_addresses)


token_default_n_decimals = 18
token_n_decimals = {
    'USDT': 6,
    'USDC': 6,
    'HUSD': 8,
    'GUSD': 2,
}
for token_symbol, token_address in token_addresses.items():
    if token_symbol in token_n_decimals:
        token_n_decimals[token_address] = token_n_decimals

# specify rari tokens as having 8 decimals
for token_address in rari_directory.rari_pool_tokens.values():
    token_n_decimals[token_address] = 8


def get_token_n_decimals(token_symbol):
    """get number of decimals tracked for a given token"""
    return token_n_decimals.get(token_symbol, token_default_n_decimals)

