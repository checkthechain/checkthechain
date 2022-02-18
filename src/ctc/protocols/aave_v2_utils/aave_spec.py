
def get_aave_address(name, network=None):
    # TODO: move to directory
    if network == 'mainnet':
        if name == 'PriceOracle':
            return '0xa50ba011c48153de246e5192c8f9258a2ba79ca9'
        elif name == 'LendingPoolProvider':
            return '0xb53c1a33016b2dc2ff3653530bff1848a515c8c5'
        elif name == 'LendingPool':
            return '0x7d2768de32b0b80b7a3454c06bdac94a69ddc7a9'
        elif name == 'IncentivesController':
            return '0xd784927ff2f95ba542bfc824c8a8a98f3495f6b5'
        else:
            raise Exception('unknown contract: ' + str(name))
    else:
        raise Exception('invalid network: ' + str(network))

