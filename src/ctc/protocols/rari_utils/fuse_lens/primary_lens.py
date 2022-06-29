from __future__ import annotations

import asyncio
import typing
from typing_extensions import TypedDict

from ctc import rpc
from ctc import spec

from .. import fuse_queries
from . import lens_abis
from . import lens_spec


async def async_get_public_pools_with_data(
    *,
    lens_address: spec.Address | None = None,
    provider: spec.ProviderReference = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> lens_spec.PublicPoolsWithData:
    if lens_address is None:
        lens_address = lens_spec.get_lens_address('primary', provider=provider)

    # on-chain implementation reverts, python implementation instead
    all_pools = await fuse_queries.async_get_all_pools(
        block=block, provider=provider
    )
    comptrollers = [pool[2] for pool in all_pools]
    coroutines = [
        _async_get_pool_summary_or_error(
            comptroller, block=block, provider=provider
        )
        for comptroller in comptrollers
    ]
    results = await asyncio.gather(*coroutines)
    summaries = [result['summary'] for result in results]
    errors = [result['error'] is not None for result in results]

    return {
        'public_pools': [
            lens_spec.fuse_pool_to_dict(pool) for pool in all_pools
        ],
        'data': summaries,
        'errored': errors,
    }


class _ReturnPoolSummaryOrError(TypedDict):
    summary: typing.Optional[lens_spec.ReturnPoolSummary]
    error: typing.Optional[str]


async def _async_get_pool_summary_or_error(
    comptroller: spec.Address,
    *,
    lens_address: spec.Address | None = None,
    provider: spec.ProviderReference = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> _ReturnPoolSummaryOrError:
    try:
        summary = await async_get_pool_summary(
            comptroller=comptroller,
            lens_address=lens_address,
            provider=provider,
            block=block,
        )
        return {'summary': summary, 'error': None}
    except spec.RpcException as e:
        return {'summary': None, 'error': e.args[0]}


async def async_get_public_pools_by_verification_with_data(
    *,
    whitelisted_admin: bool,
    lens_address: spec.Address | None = None,
    provider: spec.ProviderReference = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> lens_spec.PublicPoolsWithData:
    if lens_address is None:
        lens_address = lens_spec.get_lens_address('primary', provider=provider)

    # on-chain implementation reverts, python implementation instead
    all_pools = await fuse_queries.async_get_all_pools(
        block=block, provider=provider
    )
    comptrollers = [pool[2] for pool in all_pools]
    coroutines = [
        _async_get_pool_summary_or_error(
            comptroller, block=block, provider=provider
        )
        for comptroller in comptrollers
    ]
    results = await asyncio.gather(*coroutines)

    filtered_pools = []
    filtered_results = []
    for pool, result in zip(all_pools, results):
        if (
            result['summary'] is not None
            and result['summary']['whitelisted_admin'] == whitelisted_admin
        ):
            filtered_pools.append(pool)
            filtered_results.append(result)
    summaries = [result['summary'] for result in filtered_results]
    errors = [result['error'] is not None for result in filtered_results]

    return {
        # 'indexes': result[0],
        'public_pools': [
            lens_spec.fuse_pool_to_dict(pool) for pool in filtered_pools
        ],
        'data': summaries,
        'errored': errors,
    }


async def async_get_pools_by_account_with_data(
    account: spec.Address,
    *,
    lens_address: spec.Address | None = None,
    provider: spec.ProviderReference = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> lens_spec.ReturnPoolsBySupplierWithData:
    if lens_address is None:
        lens_address = lens_spec.get_lens_address('primary', provider=provider)
    function_abi = lens_abis.get_function_abi('getPoolsByAccountWithData')
    result = await rpc.async_eth_call(
        to_address=lens_address,
        function_abi=function_abi,
        function_parameters=[account],
        block_number=block,
        provider=provider,
    )
    return {
        'indices': result[0],
        'account_pools': [
            lens_spec.fuse_pool_to_dict(pool) for pool in result[1]
        ],
        'data': [lens_spec.fuse_pool_data_to_dict(pool) for pool in result[2]],
        'errored': result[3],
    }


async def async_get_pool_summary(
    comptroller: spec.Address,
    *,
    lens_address: spec.Address | None = None,
    provider: spec.ProviderReference = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> lens_spec.ReturnPoolSummary:
    if lens_address is None:
        lens_address = lens_spec.get_lens_address('primary', provider=provider)
    function_abi = lens_abis.get_function_abi('getPoolSummary')
    result = await rpc.async_eth_call(
        to_address=lens_address,
        function_abi=function_abi,
        function_parameters=[comptroller],
        block_number=block,
        provider=provider,
    )
    return lens_spec.return_pool_summary_to_dict(result)


async def async_get_pool_assets_with_data(
    comptroller: spec.Address,
    *,
    lens_address: spec.Address | None = None,
    provider: spec.ProviderReference = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> list[lens_spec.FusePoolAsset]:
    if lens_address is None:
        lens_address = lens_spec.get_lens_address('primary', provider=provider)
    function_abi = lens_abis.get_function_abi('getPoolAssetsWithData')
    result = await rpc.async_eth_call(
        to_address=lens_address,
        function_abi=function_abi,
        function_parameters=[comptroller],
        block_number=block,
        provider=provider,
    )
    return [lens_spec.fuse_pool_asset_to_dict(item) for item in result]


async def async_get_public_pool_users_with_data(
    *,
    max_health: int = int(1e36),
    lens_address: spec.Address | None = None,
    provider: spec.ProviderReference = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> lens_spec.ReturnPublicPoolUsersWithData:

    if lens_address is None:
        lens_address = lens_spec.get_lens_address('primary', provider=provider)

    # on-chain implementation reverts, python implementation instead
    # kwargs = {'block': block, 'provider': provider}
    max_health = int(1e36)

    all_pools = await fuse_queries.async_get_all_pools(
        block=block, provider=provider
    )
    comptrollers = [pool[2] for pool in all_pools]
    coroutines = [
        _async_get_pool_users_with_data_or_error(
            comptroller=comptroller,
            max_health=max_health,
            block=block,
            provider=provider,
        )
        for comptroller in comptrollers
    ]
    result = await asyncio.gather(*coroutines)

    users = []
    close_factors = []
    liquidation_incentives = []
    errored = []
    for subresult in result:
        if subresult['error'] is None:
            users.append(subresult['pool_users']['users'])
            close_factors.append(subresult['pool_users']['close_factor'])
            liquidation_incentives.append(
                subresult['pool_users']['liquidation_incentive']
            )
            errored.append(False)
        else:
            users.append(None)
            close_factors.append(None)
            liquidation_incentives.append(None)
            errored.append(True)

    return {
        'comptrollers': comptrollers,
        'users': users,
        'close_factors': close_factors,
        'liquidation_incentives': liquidation_incentives,
        'errored': errored,
    }


async def _async_get_pool_users_with_data_or_error(
    **kwargs: typing.Any,
) -> dict[str, typing.Any]:
    try:
        summary = await async_get_pool_users_with_data(**kwargs)
        return {'pool_users': summary, 'error': None}
    except spec.RpcException as e:
        return {'pool_users': None, 'error': e.args[0]}


async def async_get_pool_users_with_data(
    comptroller: spec.Address,
    *,
    max_health: int = int(1e36),
    lens_address: spec.Address | None = None,
    provider: spec.ProviderReference = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> lens_spec.ReturnPoolUsersWithData:
    if lens_address is None:
        lens_address = lens_spec.get_lens_address('primary', provider=provider)
    function_abi = lens_abis.get_function_abi(
        'getPoolUsersWithData',
        parameter_types=('address', 'uint256'),
    )
    result = await rpc.async_eth_call(
        to_address=lens_address,
        function_abi=function_abi,
        function_parameters=[comptroller, max_health],
        block_number=block,
        provider=provider,
    )

    return lens_spec.return_pool_users_with_data_to_dict(result)


async def async_get_pools_users_with_data(
    comptrollers: spec.Address,
    *,
    max_health: int = int(1e36),
    lens_address: spec.Address | None = None,
    provider: spec.ProviderReference = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> lens_spec.ReturnPoolsUsersWithData:
    """renamed to prevent name collision with async_get_pool_users_with_data"""

    if lens_address is None:
        lens_address = lens_spec.get_lens_address('primary', provider=provider)
    function_abi = lens_abis.get_function_abi(
        'getPoolUsersWithData',
        parameter_types=('address[]', 'uint256'),
    )
    result = await rpc.async_eth_call(
        to_address=lens_address,
        function_abi=function_abi,
        function_parameters=[comptrollers, max_health],
        block_number=block,
        provider=provider,
    )

    return {
        'users': [
            [lens_spec.fuse_pool_user_to_dict(user) for user in pool_users]
            for pool_users in result[0]
        ],
        'close_factors': result[1],
        'liquidation_incentives': result[2],
        'errored': result[3],
    }


async def async_get_pools_by_supplier(
    account: spec.Address,
    *,
    lens_address: spec.Address | None = None,
    provider: spec.ProviderReference = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> lens_spec.ReturnPoolsBySupplier:
    if lens_address is None:
        lens_address = lens_spec.get_lens_address('primary', provider=provider)
    function_abi = lens_abis.get_function_abi('getPoolsBySupplier')
    result = await rpc.async_eth_call(
        to_address=lens_address,
        function_abi=function_abi,
        function_parameters=[account],
        block_number=block,
        provider=provider,
    )
    return {
        'indices': result[0],
        'account_pools': result[1],
    }


async def async_get_pools_by_supplier_with_data(
    account: spec.Address,
    *,
    lens_address: spec.Address | None = None,
    provider: spec.ProviderReference = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> lens_spec.ReturnPoolsBySupplierWithData:
    if lens_address is None:
        lens_address = lens_spec.get_lens_address('primary', provider=provider)
    function_abi = lens_abis.get_function_abi('getPoolsBySupplierWithData')
    result = await rpc.async_eth_call(
        to_address=lens_address,
        function_abi=function_abi,
        function_parameters=[account],
        block_number=block,
        provider=provider,
    )
    return {
        'indices': result[0],
        'account_pools': [
            lens_spec.fuse_pool_to_dict(pool) for pool in result[1]
        ],
        'data': [lens_spec.fuse_pool_data_to_dict(pool) for pool in result[2]],
        'errored': result[3],
    }


async def async_get_user_summary(
    account: spec.Address,
    *,
    lens_address: spec.Address | None = None,
    provider: spec.ProviderReference = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> lens_spec.UserSummary:
    if lens_address is None:
        lens_address = lens_spec.get_lens_address('primary', provider=provider)
    function_abi = lens_abis.get_function_abi('getUserSummary')
    result = await rpc.async_eth_call(
        to_address=lens_address,
        function_abi=function_abi,
        function_parameters=[account],
        block_number=block,
        provider=provider,
    )

    return {
        'supply_balance': result[0],
        'borrow_balance': result[1],
        'error': result[2],
    }


async def async_get_pool_user_summary(
    comptroller: spec.Address,
    account: spec.Address,
    *,
    lens_address: spec.Address | None = None,
    provider: spec.ProviderReference = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> lens_spec.PoolUserSummary:
    if lens_address is None:
        lens_address = lens_spec.get_lens_address('primary', provider=provider)
    function_abi = lens_abis.get_function_abi('getPoolUserSummary')
    result = await rpc.async_eth_call(
        to_address=lens_address,
        function_abi=function_abi,
        function_parameters=[comptroller, account],
        block_number=block,
        provider=provider,
    )
    return {
        'supply_balance': result[0],
        'borrow_balance': result[1],
    }


async def async_get_whitelisted_pools_by_account(
    account: spec.Address,
    *,
    lens_address: spec.Address | None = None,
    provider: spec.ProviderReference = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> typing.Sequence[lens_spec.FusePool]:
    if lens_address is None:
        lens_address = lens_spec.get_lens_address('primary', provider=provider)
    function_abi = lens_abis.get_function_abi('getWhitelistedPoolsByAccount')
    result = await rpc.async_eth_call(
        to_address=lens_address,
        function_abi=function_abi,
        function_parameters=[account],
        block_number=block,
        provider=provider,
    )
    output = result[1]
    return typing.cast(typing.Sequence[lens_spec.FusePool], output)


async def async_get_whitelisted_pools_by_account_with_data(
    account: spec.Address,
    *,
    lens_address: spec.Address | None = None,
    provider: spec.ProviderReference = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> lens_spec.ReturnWhitelistedPoolsByAccountWithData:
    if lens_address is None:
        lens_address = lens_spec.get_lens_address('primary', provider=provider)
    function_abi = lens_abis.get_function_abi(
        'getWhitelistedPoolsByAccountWithData'
    )
    result = await rpc.async_eth_call(
        to_address=lens_address,
        function_abi=function_abi,
        function_parameters=[account],
        block_number=block,
        provider=provider,
    )

    output: lens_spec.ReturnWhitelistedPoolsByAccountWithData = {
        'indices': result[0],
        'account_pools': result[1],
        'data': result[2],
        'errored': result[3],
    }

    output['account_pools'] = [
        lens_spec.fuse_pool_to_dict(item)
        for item in typing.cast(
            typing.List[typing.Any], output['account_pools']
        )
    ]

    output['data'] = [
        lens_spec.fuse_pool_data_to_dict(item)
        for item in typing.cast(typing.List[typing.Any], output['data'])
    ]

    return output
