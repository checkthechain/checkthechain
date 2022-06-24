from __future__ import annotations

import os
from ctc import spec


def get_etherscan_key(network: spec.NetworkName) -> str | None:
    if network == 'mainnet':
        key = os.environ.get('ETHERSCAN_API_KEY')
        if key == '':
            return None
        else:
            return key
    else:
        return None
