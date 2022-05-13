from __future__ import annotations

from typing_extensions import TypedDict

import asyncio
import json
import time

from ctc import config
from ctc import evm
from ctc import spec

from . import etherscan_spec


class EtherscanRatelimit(TypedDict):
    requests_per_second: int | float
    last_request_time: int | float
    lock: asyncio.Lock | None


_etherscan_ratelimit: EtherscanRatelimit = {
    'requests_per_second': 0.2,
    'last_request_time': 0,
    'lock': None,
}


async def async_get_contract_abi(
    contract_address: spec.Address,
    network: spec.NetworkReference | None = None,
    verbose: bool = True,
) -> spec.ContractABI:
    """fetch contract abi using etherscan"""

    import aiohttp

    # process inputs
    if network is None:
        network = config.get_default_network()
    if network != 'mainnet':
        raise Exception('etherscan is only for mainnnet')
    if not evm.is_address_str(contract_address):
        raise Exception('not a valid address: ' + str(contract_address))

    if verbose:
        print('fetching abi from etherscan:', contract_address)

    # create lock
    lock = _etherscan_ratelimit['lock']
    if lock is None:
        lock = asyncio.Lock()
        _etherscan_ratelimit['lock'] = lock

    # acquire lock
    async with lock:

        # ratelimit
        now = time.time()
        time_since_last = now - _etherscan_ratelimit['last_request_time']
        seconds_per_request = 1 / _etherscan_ratelimit['requests_per_second']
        time_to_sleep = seconds_per_request - time_since_last
        if time_to_sleep > 0:
            if verbose:
                print(
                    'etherscan ratelimit hit, sleeping for '
                    + str(time_to_sleep)
                    + ' seconds'
                )
            await asyncio.sleep(time_to_sleep)

        # create url
        url_template = etherscan_spec.abi_url_templates['mainnet']
        abi_endpoint = url_template.format(address=contract_address)

        # make request
        _etherscan_ratelimit['last_request_time'] = time.time()
        async with aiohttp.ClientSession() as session:
            async with session.get(abi_endpoint) as response:
                content = await response.text()

        # process request
        if content == 'Contract source code not verified':
            raise spec.AbiNotFoundException()
        abi = json.loads(content)
        if isinstance(abi, dict) and abi.get('status') == '0':
            raise Exception(
                'could not obtain contract abi from etherscan for '
                + str(contract_address)
            )

    return abi
