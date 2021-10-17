from ctc import evm


fei_addresses = {
    #
    # core + governance
    'Core': '0x8d5ed43dca8c2f7dfb20cf7b53cc7e593635d7b9',
    'Tribe': '0xc7283b66eb1eb5fb86327f08e1b5816b0720212b',
    'Fei DAO': '0x0bef27feb58e857046d630b2c03dfb7bae567494',
    'Fei DAO Timelock': '0xd51dbA7a94e1adEa403553A8235C302cEbF41a3c',
    'Fei': '0x956f47f50a910163d8bf957cf5846d573e7f87ca',
    'RatioPCVController': '0xB1410aeCe2c65fE9e107c58b5aa32e91B18f0BC7',
    #
    # stability + liquidity
    'EthBondingCurve': '0xB783c0E21763bEf9F2d04E6499abFbe23AdB7e1F',
    'DAIBondingCurve': '0xC0afe0E649e32528666F993ce63822c3840e941a',
    'RAIBondingCurve': '0x25d60212D47Dd8F6Ff0469367E4c6C98Cd3411A5',
    'DPIBondingCurve': '0xbf5721c5e1c370f6f1a3e21b3972e0ace93a1e84',
    'DPISushiswapPCVDeposit': '0x902199755219A9f8209862d09F1891cfb34F59a3',
    'IndexSnapshotDelegatorPCVDeposit': '0x0ee81df08B20e4f9E0F534e50da437D24491c4ee',
    'EthUniswapPCVDeposit': '0x15958381E9E6dc98bD49655e36f524D2203a28bD',
    'EthReserveStabilizer': '0x17305f0e18318994a57b494078CAC866A857F7b6',
    #
    # oracles
    'EthUsdChainlinkOracleWrapper': '0xCd3c40AE1256922BA16C7872229385E20Bc8351e',
    'FeiEthChainlinkOracleWrapper': '0x060Be7B51F78DFFd04749332fd306BA1228e7444',
    'FeiUsdCompositeOracle': '0x8721f9EAba0B9081069970bCBce38763D3D4f28E',
    'DaiUsdChainlinkOracleWrapper': '0x231ada12e273edf3fa54cbd90c5c1a73129d5bb9',
    'DpiUsdChainlinkOracleWrapper': '0xb594d2bd55ede471e16b92ae6f7651648da871c3',
    'RaiEthChainlinkOracleWrapper': '0x3d49573ee6afcbde606f8a1c2aa1c498048e7190',
    'RaiUsdCompositeOracle': '0x392b1d29edab680c5ca778d3a32b8284859bfbb0',
    #
    # incentives
    'TribalChief': '0x9e1076cc0d19f9b0b8019f384b0a29e48ee46f7f',
    'TribeErc20Dripper': '0x3Fe0EAD3500e767F0F8bC2d3B5AF7755B1b21A6a',
    'TribeAaveIncentrivesController': '0xDee5c1662bBfF8f80f7c572D8091BF251b3B0dAB',
    'fTRIBEStakedTokenWrapper': '0xd81Be1B9A7895C996704A8DDa794BbA4454EeB90',
    'FeiRariRewardsDistributorDelegator': '0x73F16f0c0Cd1A078A54894974C5C054D8dC1A3d7',
    'FeiRariRewardsDistributorAdmin': '0x4e979E8b136Cd7BdEBB83ea50a599C3BED1e15c0',
    'FeiRariTribeAutoRewardsDistributor': '0x61Be49Dfbd869a601FEa076E1A1379903e61a895',
    #
    # yield PCV Deployments
    'FeiRariFeifFEI8': '0xd8553552f8868C1Ef160eEdf031cF0BCf9686945',
    'FeiRariFeiInterestRateModel': '0x8f47Be5692180079931e2F983Db6996647AbA0A5',
    'FeiRariTribefTribe8': '0xFd3300A9a74b3250F1b2AbC12B47611171910b07',
    'FeiRariTribeInterestRateModel': '0x075538650a9c69ac8019507A7DD1BD879B12c1d7',
    'FeiRariEthfEth8': '0xbB025D470162CC5eA24daF7d4566064EE7f5F111',
    'FeiRariEthInterestRateModel': '0xbAB47e4B692195BF064923178A90Ef999A15f819',
    'FeiRariDaifDai8': '0x7e9cE3CAa9910cc048590801e64174957Ed41d43',
    'FeiRariDaiInterestRateModel': '0xEDE47399e2aA8f076d40DC52896331CBa8bd40f7',
    'FeiRariFeiPcvDeposit': '0x37349d9cc523D28e6aBFC03fc5F44879bC8BfFD9',
    'FusePool6FeiPcvDeposit': '0xB51f09B6F103D697dc5d64DC904Ad6a2Dad39987',
    'FusePool7FeiPcvDeposit': '0x74B235Fef146cDB5BE0D3786a9f3774674b3615E',
    'FusePool24FeiPcvDeposit': '0x1434F99EDB2bD03DECCCFe21288767b8324B7403',
    'CreamFeiPcvDeposit': '0x243C601CC5DaA3Ac250B14509804188347bd2aFB',
    'FusePoolPartyFeiPcvDeposit': '0x5A8CB4556e5D5935Af06beab8292905f48131479',
    'IndexCoopFusePoolFeiPcvDeposit': '0xD6960adba53212bBE96E54a7AFeDA2066437D000',
    'IndexCoolFusePoolDpiPcvDeposit': '0x3dD3d945C4253bAc5B4Cc326a001B7d3f9C4DD66',
    'CompoundDaiPcvDeposit': '0xe0f73b8d76D2Ad33492F995af218b03564b8Ce20',
    'FusePool9FeiPcvDeposit': '0xF2D8beE45f29A779cFB9F04ac233E703974a2C53',
    'FusePool25FeiPcvDeposit': '0xe1662531aA5de1DAD8ab5B5756b8F6c8F3C759Ca',
    'FusePool26FeiPcvDeposit': '0xFdCc96967C86250f333cE52Ba706Ec2961c3302f',
    'FusePool27FeiPcvDeposit': '0x91f50E3183a8CC30D2A981C3aFA85A2Bf6691c67',
    'FusePool9RaiPcvDeposit': '0x9aAdFfe00eAe6d8e59bB4F7787C6b99388A6960D',
    'AaveRaiPcvDeposit': '0xd2174d78637a40448112aa6B30F9B19e6CF9d1F9',
    'CompoundEthPcvDeposit': '0x4fCB1435fD42CE7ce7Af3cB2e98289F79d2962b3',
    'AaveEthPcvDeposit': '0x5B86887e171bAE0C2C826e87E34Df8D558C079B9',
    'EthLidoPCVDeposit': '0xac38ee05c0204a1e119c625d0a560d6731478880',
    #
    # multisig addresses
    'TribalChiefOptimisticMultisig': '0x35ED000468f397AA943009bD60cc6d2d9a7d32fF',
    'TribalChiefOptimisticTimelock': '0xbC9C084a12678ef5B516561df902fdc426d95483',
    'GuardianMultisig': '0xB8f482539F2d3Ae2C9ea6076894df36D1f632775',
    #
    # external addresses
    'FeiEthUniV2Pair': '0x94B0A3d511b6EcDb17eBF877278Ab030acb0A878',
    'FeiTribeUniV2Pair': '0x9928e4046d7c6513326cCeA028cD3e7a91c7590A',
    'Fei3CrvCurvePool': '0x06cb22615BA53E60D67Bf6C341a0fD5E718E1655',
    'ChainlinkFeiEth': '0x7F0D2c2838c6AC24443d13e23d99490017bDe370',
    'ChainlinkTribeEth': '0x84a24deCA415Acc0c395872a9e6a63E27D6225c8',
    #
    # additional
    'FeiRouter': '0x9271d303b57c204636c38df0ed339b18bf98f909',
    'GenesisGroup': '0xbffb152b9392e38cddc275d818a3db7fe364596b',
    'IDO': '0x7d809969f6a04777f0a87ff94b57e56078e5fe0f',
    'TimelockedDelegator': '0x38afbf8128cc54323e216acde9516d281c4f1e5f',
    #
    # deprecated
    'FeiRewardsDistributor': '0xef1a94af192a88859eaf3f3d8c1b9705542174c5',
    'FeiStakingRewards': '0x18305daae09ea2f4d51faa33318be5978d251abd',
    'BondingCurveOracle': '0x89714d3ac9149426219a3568543200d1964101c4',
    'EthPCVDepositAdapter': '0xb72dded4fa321e093e2083b596404a56ffc5b574',
    'EthPCVDripper': '0xda079a280fc3e33eb11a78708b369d5ca2da54fe',
    'EthUniswapPCVController': '0x0760dfe09bd6d04d0df9a60c51f01ecedceb5132',
    'UniswapIncentive': '0xfe5b6c2a87a976dce20130c423c679f4d6044cd7',
    'UniswapOracle': '0x087f35bd241e41fc28e43f0e8c58d283dd55bd65',
}
address_to_fei_name = evm.create_reverse_address_map(fei_addresses)

fei_contract_to_aliases = {
    'GovernorAlpha': 'Fei DAO',
    'Timelock': 'Fei DAO Timelock',
}


def get_fei_address(contract_name, block=None):
    if contract_name in fei_contract_to_aliases:
        contract_name = fei_contract_to_aliases[contract_name]
    if block is not None:

        # core + governance

        if contract_name == 'Fei DAO':
            if block < 13369671:
                return '0xe087f94c3081e1832dc7a22b48c6f2b5faae579b'

        elif contract_name == 'Fei DAO Timelock':
            if block < 13395910:
                return '0x639572471f2f318464dc01066a56867130e45e25'

        elif contract_name == 'RatioPCVController':
            if block < 13392602:
                return '0xfc1ad6eb84351597cd3b9b65179633697d65b920'

        # stability + liquidity

        elif contract_name == 'EthBondingCurve':
            if block < 13392602:
                return '0xe1578b4a32eaefcd563a9e6d0dc02a4213f673b7'

        elif contract_name == 'EthUniswapPCVDeposit':
            if block < 12466522:
                return '0x9b0C6299D08fe823f2C0598d97A1141507e4ad86'
            elif block < 13392602:
                return '0x5d6446880fcd004c851ea8920a628c70ca101117'

        elif contract_name == 'EthReserveStabilizer':
            if block < 13123828:
                return '0xa08a721dfb595753fff335636674d76c455b275c'

        # other

        elif contract_name == 'EthUniswapPCVController':
            if block < 12337811:
                return '0x0760dfe09bd6d04d0df9a60c51f01ecedceb5132'

    return fei_addresses[contract_name]


def get_fei_contract_name(fei_name):
    if fei_name == 'Fei DAO':
        return 'GovernorAlpha'
    elif fei_name == 'Fei DAO Timelock':
        return 'Timelock'
    elif fei_name in fei_addresses:
        return fei_name
    else:
        raise Exception('unknown name: ' + fei_name)


def get_fei_contract_names():
    extra = ['GovernorAlpha', 'Timelock']
    return list(fei_addresses.keys()) + extra


other_addresses = {
    'ethereum_root': '0x0000000000000000000000000000000000000000',
}

fei_blocks = {
    'fgen_creation_block': 12125748,
    'end_fei_genesis_block': 12125707,
    'fip2_executed': 12337811,
    'fip5_executed': 12466522,
    'fip3_executed': 12492236,
}

