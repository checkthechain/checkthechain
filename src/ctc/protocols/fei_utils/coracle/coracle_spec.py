
usd_token = '0x1111111111111111111111111111111111111111'


coracle_addresses = {
    'StaticPCVDepositWrapper': '0x8B41DcEfAe6064E6bc2A9B3ae20141d23EFD6cbd',
    'CollateralizationOracle': '0xFF6f59333cfD8f4Ebc14aD0a0E181a83e655d257',
    'CollateralizationOracleWrapper_TransparentUpgradeableProxy': '0xd1866289B4Bd22D453fFF676760961e0898EE9BF',
    'CollateralizationOracleWrapper_ProxyImplementation': '0x656aA9c9875eB089b11869d4730d6963D25E76ad',
    'ProxyAdmin': '0xf8c2b645988b7658e7748ba637fe25bdd46a704a',
}
coracle_addresses = {k: v.lower() for k, v in coracle_addresses.items()}


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

