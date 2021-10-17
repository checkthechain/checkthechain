
# for tokens whose project name is the same as the token name
token_contract_files = {
    'USDC': 'FiatTokenProxy',
    'WETH': 'WETH9',
    'CHI': 'ChiToken',
    'DAI': 'Dai',
    'USDT': 'TetherToken',
    'AAVE': 'InitializableAdminUpgradeabilityProxy',
    'BRIBE': 'BribeToken',
    'LUSD': 'LUSDToken',
    'FRAX': 'FRAXStablecoin',
    'MKR': 'DSToken',
    'WBTC': 'WBTC',
}


# each entry in is in form: (project_name, contract_name[, common_name])
contract_address_metadata = {
    '0x6c3f90f043a72fa612cbac8115ee7e52bde6e490': (
        'crv',
        'Vyper_contract',
        '3CRV',
    ),
    '0x11111112542d85b3ef69ae05771c2dccff4faa26': (
        '1inch',
        'AggregationRouterV3',
    ),
    '0x61935cbdd02287b511119ddb11aeb42f1593b7ef': (
        '0x',
        'Exchange.3',
    ),
    '0x080bf510fcbf18b91105470639e9561022937712': (
        '0x',
        'Exchange.2.1',
    ),
    '0xdef1c0ded9bec7f1a1670819833240f027b25eff': (
        '0x',
        'ZeroEx',
    ),
    '0xa356867fdcea8e71aeaf87805808803806231fdc': (
        'dodo',
        'DODOV2Proxy02',
    ),
    '0xc9f93163c99695c6526b799ebca2207fdf7d61ad': (
        'dodo',
        'DODO',
    ),
    '0x43dfc4159d86f3a37a5a4b3d4580b888ad7d4ddd': (
        'dodo',
        'DODOToken',
    ),
    '0xaed7384f03844af886b830862ff0a7afce0a632c': (
        'dodo',
        'DODOMine',
    ),
    '0x6d9893fa101cd2b1f8d1a12de3189ff7b80fdc10': (
        'zapper',
        'UniswapV2_ZapIn_General_V5',
    ),
    '0x2aa63cd0b28fb4c31fa8e4e95ec11815be07b9ac': (
        'unknown',
        'PolyWrapper.0x2aa63c',
    ),
    '0xd291328a6c202c5b18dcb24f279f69de1e065f70': (
        'zerion',
        'Core',
    ),
    '0xd784927ff2f95ba542bfc824c8a8a98f3495f6b5': (
        'aave',
        'InitializableImmutableAdminUpgradeabilityProxy',
    ),
    '0x250e76987d838a75310c34bf422ea9f1ac4cc906': (
        'poly_network',
        'PolyNetworkBridge',
    ),
    '0xc69ddcd4dfef25d8a793241834d4cc4b3668ead6': (
        'saddle',
        'SwapFlashLoan',
        'd4',
    ),
    '0x0639076265e9f88542c91dcdeda65127974a5ca5': (
        'saddle',
        'CommunalFarm_SaddleD4',
        'd4_rewards',
    ),
    '0x8eca806aecc86ce90da803b080ca4e3a9b8097ad': (
        'zkswap',
        'Proxy',
    ),
    '0xc1513c1b0b359bc5acf7b772100061217838768b': (
        'pickle',
        'PickleJar',
    ),
    '0x838bf9e95cb12dd76a54c9f9d2e3082eaf928270': (
        'unknown',
        'Unknown.0x838bf9',
    ),
    '0x22f9dcf4647084d6c31b2765f6910cd85c178c18': (
        'unknown',
        'FlashWallet.0x22f9dc',
    ),
    '0x881d40237659c251811cec9c364ef91dc08d300c': (
        'unknown',
        'Unknown.0x881d40',
    ),
    '0xbc6da0fe9ad5f3b0d58160288917aa56653660e9': (
        'alchemix',
        'AlToken',
        'alUSD',
    ),
    '0x18aaa7115705e8be94bffebde57af9bfc265b998': (
        'audius',
        'AudiusAdminUpgradeabilityProxy',
        'AUDIO',
    ),
    '0xe4815ae53b124e7263f08dcdbbb757d41ed658c6': (
        'zkswap',
        'ZksToken',
        'ZKS',
    ),
    '0x3432b6a60d23ca0dfca7761b7ab56459d9c964d0': (
        'frax',
        'FRAXShares',
        'FXS',
    ),
    '0xc36442b4a4522e871399cd717abdd847ab11fe88': (
        'uniswap',
        'NonfungiblePositionManager',
        'uniswap_v3_position',
    ),
}

