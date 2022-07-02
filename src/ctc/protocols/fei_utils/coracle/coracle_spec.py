from __future__ import annotations

import typing

from ctc import spec


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
    '0x2c47fef515d2c70f2427706999e158533f7cf090': {
        'name': 'Tribe Turbo',
        'platform': 'Rari Fuse',
    },
    '0xb4ffd10c4c290dc13e8e30bf186f1509001515fd': {
        'name': 'Fuse Pool 25',
        'platform': 'Rari Fuse',
    },
    '0x4a5af5a124e672c156241b76cad4e41d09dd4883': {
        'name': 'Fuse Pool 72',
        'platform': 'Rari Fuse',
    },
    '0x4e119714f625b2e82e5fb5a7e297978f020ea51e': {
        'name': 'Fuse Pool 28',
        'platform': 'Rari Fuse',
    },
    '0x05e2e93cfb0b53d36a3151ee727bb581d4b918ce': {
        'name': 'Fuse Pool 31',
        'platform': 'Rari Fuse',
    },
    '0xd6598a23418c7fef7c0dc863265515b623b720f9': {
        'name': 'Fuse Pool 8',
        'platform': 'Rari Fuse',
    },
    '0x76dfcf06e7d7b8248094dc319b284fb244f06309': {
        'name': 'Fuse Pool 79',
        'platform': 'Rari Fuse',
    },
    '0x81dcb06ea4db474d1506ca6275ff7d870ba3a1be': {
        'name': 'Fuse Pool 31',
        'platform': 'Rari Fuse',
    },
    '0xb13c755107301ebfed6a93190acde09281b2f8a5': {
        'name': 'Fuse Pool 7',
        'platform': 'Rari Fuse',
    },
    '0x07f2dd7e6a78d96c08d0a8212f4097dcc129d629': {
        'name': 'Fuse Pool 18',
        'platform': 'Rari Fuse',
    },
    '0xe2e35097638f0ff2eeca2ef70f352be37431945f': {
        'name': 'Fuse Pool 27',
        'platform': 'Rari Fuse',
    },
    '0xb0d5eba35e1cece568096064ed68a49c6a24d961': {
        'name': 'Fuse Pool 28',
        'platform': 'Rari Fuse',
    },
    '0x7aa4b1558c3e219cfffd6a356421c071f71966e7': {
        'name': 'Fuse Pool 6',
        'platform': 'Rari Fuse',
    },
    '0x2296a2417d1f02d394ab22af794a0f426ed53436': {
        'name': 'Fuse Pool 91',
        'platform': 'Rari Fuse',
    },
    # '0xff419bc27483edb94b7ad5c97b7fab5db323c7e0': {
    #     'name': 'CREAM',
    #     'platform': 'CREAM',
    # },
    '0x7e39bba9d0d967ee55524fae9e54900b02d9889a': {
        'name': 'Fuse Pool 19',
        'platform': 'Rari Fuse',
    },
    '0x96a657ee40a79a964c6b4ea551c895d98e885a75': {
        'name': 'Fuse Pool 9',
        'platform': 'Rari Fuse',
    },
    '0x7eb88140af813294aedce981b6ac08fcd139d408': {
        'name': 'OA Account',
        'platform': 'OA Account',
    },
    '0x508f6fbd78b6569c29e9d75986a51558de9e5865': {
        'name': 'Fuse Pool 24',
        'platform': 'Rari Fuse',
    },
    '0x82aebee64a52180d8541eb601a8381e012a1ed04': {
        'name': 'Fuse Pool 26',
        'platform': 'Rari Fuse',
    },
    '0x61d26126d2f8a44b41c1d8e1b1f276551dc8eec6': {
        'name': 'Fuse Pool 90',
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
    '0x673f7dfa863b611de657759aede629b260f4e682': {
        'name': 'Balancer Pool2',
        'platform': 'Balancer',
    },
    '0xd8eb546726d449fc1ded06dfeca800a2fa8bb930': {
        'name': 'Balancer Pool2',
        'platform': 'Balancer',
    },
    '0x7ac2ab8143634419c5bc230a9f9955c3e29f64ef': {
        'name': 'Uniswap FEI-agEUR',
        'platform': 'Uniswap V2',
    },
    '0x2a188f9eb761f70ecea083ba6c2a40145078dfc2': {
        'name': 'FEI-DAI PSM',
        'platform': 'Fei',
    },
    '0x98e5f5706897074a4664dd3a32eb80242d6e694b': {
        'name': 'FEI-ETH PSM',
        'platform': 'Fei',
    },
    '0xb0e731f036adfdec12da77c15aab0f90e8e45a0e': {
        'name': 'FEI-LUSD PSM',
        'platform': 'Fei',
    },
    '0xc5bb8f0253776bec6ff450c2b40f092f7e7f5b57': {
        'name': 'Balancer FEI-WETH',
        'platform': 'Balancer',
    },
    '0x89dfbc12001b41985efabd7dfcae6a77b22e4ec3': {
        'name': 'Balancer FEI-TRIBE',
        'platform': 'Balancer',
    },
    '0xec54148cbc47bff8fcc5e04e5e8083adb8af9ad9': {
        'name': 'Fuse Pool 90 FEI',
        'platform': 'Rari Fuse',
    },
    '0xb3a026b830796e43bfc8b135553a7573538ab341': {
        'name': 'Fuse Pool 79 FEI',
        'platform': 'Rari Fuse',
    },
    '0xa62ddde8f799873e6fcdbb3acbba75da85d9dcde': {
        'name': 'Fuse Pool 128 FEI',
        'platform': 'Rari Fuse',
    },
    '0xa2bdbcb95d31c85bae6f0fa42d55f65d609d94ee': {
        'name': 'Fuse Pool 22 FEI',
        'platform': 'Rari Fuse',
    },
    '0x395b1bc1800fa0ad48ae3876e66d4c10d297650c': {
        'name': 'Fuse Pool 72 FEI',
        'platform': 'Rari Fuse',
    },
    '0xd2554839c2e8a87dd2cddd013ef828b6534abc26': {
        'name': 'Uniswap FEI-agEUR',
        'platform': 'Uniswap V2',
    },
    '0xb80b3dc4f8b30589477b2ba0e4ef2b8224bdf0a5': {
        'name': 'Compound cFEI',
        'platform': 'Compound',
    },
    '0x1370ca8655c255948d6c6110066d78680601b7c2': {
        'name': 'Fuse Pool 156',
        'platform': 'Rari Fuse',
    },
    '0x564efce5c6873219a7fbe450187c23254e3d62a4': {
        'name': 'Tribe VOLT Reserves',
        'platform': 'Tribe',
    },
    '0x8cba3149b95084a61bbab9e01110b0fb92c9a289': {
        'name': 'Balancer veBAL',
        'platform': 'Balancer',
    },
    '0xe8633c49ace655eb4a8b720e6b12f09bd3a97812': {
        'name': 'FEI-agEUR LP',
        'platform': 'Angle',
    },
}

deposit_names = {
    # BAL
    '0xcd1ac0014e2ebd972f40f24df1694e6f528b2fd4': 'Balancer BAL-WETH',
    # LUSD
    '0xf846ee6e8ee9a6fbf51c7c65105cabc041c048ad': 'Fuse Pool 8 LUSD',
    '0x374628ebe7ef6aca0574e750b618097531a26ff8': 'B Protocol LUSD',
    '0x6026a1559cdd44a63c5ca9a078cc996a9eb68abb': 'Fuse Pool 7 LUSD',
    '0x8c51e4532cc745cf3dfec5cebd835d07e7ba1002': 'Fuse Pool 91 LUSD',
    # DPI
    '0x9a774a1b1208c323eded05e6daf592e6e59caa55': 'Fuse Pool 19 DPI',
    '0xb250926e75b1cc6c53e77bb9426baac14ab1e24c': 'DAO Timelock DPI',
    # RAI
    '0x7339ca4ac94020b83a34f5edfa6e0f26986c434b': 'DAO Timelock RAI',
    '0x1267b39c93711dd374deab15e0127e4adb259be0': 'AAVE RAI',
    '0xcce230c087f31032fc17621a2cf5e425a0b80c96': 'Fuse Pool 9 RAI',
    '0x5dde9b4b14edf59cb23c1d4579b279846998205e': 'RAI PSM',
    # DAI
    '0x9cc46ab5a714f7cd24c59f33c5769039b5872491': 'Fuse Pool 8 DAI',
    '0xfde7077aaecdaf2c4b85261aa858c96a7e737a61': 'Compound DAI',
    # WETH
    '0x5e9fa7d783a7f7d4626ce450c8bd2ebbb26dfdb2': 'DAO Timelock ETH',
    '0xc68412b72e68c30d4e6c0854b439cbbe957146e4': 'Fuse Pool 146 ETH',
    '0x43ef03755991056681f01ee2182234ef6af1f658': 'AAVE ETH',
    '0x0735e14d28ed395048d5fa4a8dbe6e6eb9fc0470': 'Compound ETH',
    '0xa271ff86426c7fdaaae72603e6ce68c892d69ed7': 'Lido stETH',
    '0x0961d2a545e0c1201b313d14c57023682a546b9d': 'Tokemak tWETH',
    # agEUR
    '0x485d23ce5725ecde46ca9033012984d90b514ffd': 'DAO Timelock agEUR',
    # CREAM
    '0x3a1838ac9eca864054bebb82c32455dd7d7fc89c': 'CREAM Hack Repayment',
}


def get_coracle_address(
    wrapper: bool = False,
    block: spec.BlockNumberReference | None = None,
) -> spec.Address:

    if wrapper:
        return coracle_addresses[
            'CollateralizationOracleWrapper_TransparentUpgradeableProxy'
        ]
    else:
        return coracle_addresses['CollateralizationOracle']


def get_coracle_address_by_block(
    blocks: typing.Sequence[spec.BlockNumberReference],
    wrapper: bool = False,
) -> typing.Sequence[spec.Address]:
    return [
        get_coracle_address(wrapper=wrapper, block=block) for block in blocks
    ]
