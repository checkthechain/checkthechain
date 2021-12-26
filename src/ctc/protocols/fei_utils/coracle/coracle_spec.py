
usd_token = '0x1111111111111111111111111111111111111111'


coracle_addresses = {
    'StaticPCVDepositWrapper': '0x8B41DcEfAe6064E6bc2A9B3ae20141d23EFD6cbd',
    'CollateralizationOracle': '0xFF6f59333cfD8f4Ebc14aD0a0E181a83e655d257',
    'CollateralizationOracleWrapper_TransparentUpgradeableProxy': '0xd1866289B4Bd22D453fFF676760961e0898EE9BF',
    'CollateralizationOracleWrapper_ProxyImplementation': '0x656aA9c9875eB089b11869d4730d6963D25E76ad',
    'ProxyAdmin': '0xf8c2b645988b7658e7748ba637fe25bdd46a704a',
}
coracle_addresses = {k: v.lower() for k, v in coracle_addresses.items()}

token_aliases = {
    'WETH': 'ETH',
    'USD': 'Misc',
}
skip_tokens = [
    'CREAM',
]

deposit_metadata = {
    '0xb4ffd10c4c290dc13e8e30bf186f1509001515fd': {
        'name': 'Fuse Barnbridge Pool 25',
        'platform': 'Rari Fuse',
    },
    '0x4a5af5a124e672c156241b76cad4e41d09dd4883': {
        'name': 'Fuse Forex Pool 72',
        'platform': 'Rari Fuse',
    },
    '0x4e119714f625b2e82e5fb5a7e297978f020ea51e': {
        'name': 'Fuse G-UNI Pool 28',
        'platform': 'Rari Fuse',
    },
    '0x05e2e93cfb0b53d36a3151ee727bb581d4b918ce': {
        'name': 'Fuse NFTX Pool 31',
        'platform': 'Rari Fuse',
    },
    '0xd6598a23418c7fef7c0dc863265515b623b720f9': {
        'name': 'Fuse Fei Pool 8',
        'platform': 'Rari Fuse',
    },
    '0x76dfcf06e7d7b8248094dc319b284fb244f06309': {
        'name': 'Fuse Fei Pool 79',
        'platform': 'Rari Fuse',
    },
    '0x81dcb06ea4db474d1506ca6275ff7d870ba3a1be': {
        'name': 'Fuse NFTX Pool 31',
        'platform': 'Rari Fuse',
    },
    '0xb13c755107301ebfed6a93190acde09281b2f8a5': {
        'name': 'Fuse UpOnly Pool 7',
        'platform': 'Rari Fuse',
    },
    '0x07f2dd7e6a78d96c08d0a8212f4097dcc129d629': {
        'name': 'Fuse Ohm Pool 18',
        'platform': 'Rari Fuse',
    },
    '0xe2e35097638f0ff2eeca2ef70f352be37431945f': {
        'name': 'Fuse StakeDAO Pool 27',
        'platform': 'Rari Fuse',
    },
    '0xb0d5eba35e1cece568096064ed68a49c6a24d961': {
        'name': 'Fuse G-UNI Pool 28',
        'platform': 'Rari Fuse',
    },
    '0x7aa4b1558c3e219cfffd6a356421c071f71966e7': {
        'name': 'Fuse Tetranode\'s Locker Pool 6',
        'platform': 'Rari Fuse',
    },
    '0x2296a2417d1f02d394ab22af794a0f426ed53436': {
        'name': 'Fuse Liquity Pool 91',
        'platform': 'Rari Fuse',
    },
    # '0xff419bc27483edb94b7ad5c97b7fab5db323c7e0': {
    #     'name': 'CREAM',
    #     'platform': 'CREAM',
    # },
    '0x7e39bba9d0d967ee55524fae9e54900b02d9889a': {
        'name': 'Fuse Index Coop Pool 19',
        'platform': 'Rari Fuse',
    },
    '0x96a657ee40a79a964c6b4ea551c895d98e885a75': {
        'name': 'Fuse Stable Asset Pool 9',
        'platform': 'Rari Fuse',
    },
    '0x7eb88140af813294aedce981b6ac08fcd139d408': {
        'name': 'OA Account',
        'platform': 'OA Account',
    },
    '0x508f6fbd78b6569c29e9d75986a51558de9e5865': {
        'name': 'Fuse Harvest Pool 24',
        'platform': 'Rari Fuse',
    },
    '0x82aebee64a52180d8541eb601a8381e012a1ed04': {
        'name': 'Fuse Tokemak Pool 26',
        'platform': 'Rari Fuse',
    },
    '0x61d26126d2f8a44b41c1d8e1b1f276551dc8eec6': {
        'name': 'Fuse Float Pool 90',
        'platform': 'Rari Fuse',
    },
    '0x107460564896377ba6cdcc7516c7eab65e32e360': {
        'name': 'Balancer FEI-TRIBE LBP',
        'platform': 'Balancer',
    },
    '0xfac571b6054619053ac311da8112939c9a374a85': {
        'name': 'Aave V2 FEI Pool',
        'platform': 'Aave',
    },
    '0x15958381e9e6dc98bd49655e36f524d2203a28bd': {
        'name': 'Uniswap FEI-ETH',
        'platform': 'Uniswap V2',
    },
    '0x5ae217de26f6ff5f481c6e10ec48b2cf2fc857c8': {
        'name': 'Curve d3',
        'platform': 'Curve',
    },
    '0x902199755219a9f8209862d09f1891cfb34f59a3': {
        'name': 'Sushiswap FEI-DPI',
        'platform': 'Sushi',
    },
    '0x1f05b337cb16cea2a1c638ba9b9571f0cf4a5612': {
        'name': 'Balancer FEI-USD',
        'platform': 'Balancer',
    },
    '0x7ac2ab8143634419c5bc230a9f9955c3e29f64ef': {
        'name': 'Uniswap FEI-agEUR',
        'platform': 'Uniswap V2',
    },
}


def get_coracle_address(wrapper=False, block=None, blocks=None):

    if blocks is not None:
        return [
            get_coracle_address(wrapper=wrapper, block=block)
            for block in blocks
        ]

    if wrapper:
        return coracle_addresses[
            'CollateralizationOracleWrapper_TransparentUpgradeableProxy'
        ]
    else:
        return coracle_addresses['CollateralizationOracle']

