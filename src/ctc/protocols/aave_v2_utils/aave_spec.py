from __future__ import annotations

from ctc import spec


def get_aave_address(
    name: str,
    network: spec.NetworkReference | None = None,
) -> spec.Address:
    # TODO: move to directory
    if network in ('mainnet', 1):
        if name == 'PriceOracle':
            return '0xa50ba011c48153de246e5192c8f9258a2ba79ca9'
        elif name == 'LendingPoolProvider':
            return '0xb53c1a33016b2dc2ff3653530bff1848a515c8c5'
        elif name == 'LendingPool':
            return '0x7d2768de32b0b80b7a3454c06bdac94a69ddc7a9'
        elif name == 'IncentivesController':
            return '0xd784927ff2f95ba542bfc824c8a8a98f3495f6b5'
        elif name == 'Collector':
            return '0x464C71f6c2F760DdA6093dCB91C24c39e5d6e18c'
        else:
            raise Exception('unknown contract: ' + str(name))
    else:
        raise Exception('invalid network: ' + str(network))
