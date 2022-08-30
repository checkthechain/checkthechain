from __future__ import annotations

import typing

from ctc import spec
from ctc.toolbox import nested_utils

from . import coracle_spec
from . import coracle_deposits
from . import coracle_balances


#
# # fei deposits
#


async def async_get_fei_deposit_balances(
    *,
    block: spec.BlockNumberReference = 'latest',
    provider: spec.ProviderReference = None,
    normalize: bool = True,
) -> dict[spec.ContractAddress, typing.Union[int, float]]:

    FEI = '0x956f47f50a910163d8bf957cf5846d573e7f87ca'
    fei_deposits = await coracle_deposits.async_get_token_deposits(
        token=FEI,
        block=block,
        provider=provider,
    )

    fei_balances = await coracle_balances.async_get_deposits_balances(
        deposits=fei_deposits,
        block=block,
        provider=provider,
    )

    non_fei_balances = await _async_get_non_fei_deposits_fei_balances(
        block=block, provider=provider
    )
    fei_deposits = fei_deposits + tuple(non_fei_balances.keys())
    fei_balances.extend(non_fei_balances.values())

    result: typing.Union[list[int], list[float]]
    if normalize:
        result = [balance / 1e18 for balance in fei_balances]
    else:
        result = fei_balances

    return dict(zip(fei_deposits, result))


async def _async_get_non_fei_deposits_fei_balances(
    block: spec.BlockNumberReference,
    *,
    provider: spec.ProviderReference = None,
) -> dict[str, int]:

    tokens_deposits = await coracle_deposits.async_get_tokens_deposits(
        block=block
    )

    non_fei_deposits: typing.MutableSequence[spec.Address] = []
    for token, deposits in tokens_deposits.items():
        non_fei_deposits.extend(deposits)

    balances = (
        await coracle_balances.async_get_deposits_resistant_balances_and_fei(
            deposits=non_fei_deposits,
            block=block,
        )
    )

    fei_balances = [balance[1] for balance in balances]

    return dict(zip(non_fei_deposits, fei_balances))


async def async_get_fei_deposit_balances_by_block(
    *,
    blocks: typing.Sequence[spec.BlockNumberReference],
    provider: spec.ProviderReference = None,
) -> dict[spec.ContractAddress, list[typing.Union[int, float]]]:
    from ctc.toolbox import async_utils

    coroutines = [
        async_get_fei_deposit_balances(block=block, provider=provider)
        for block in blocks
    ]
    results = await async_utils.async_gather_coroutines(*coroutines)
    return nested_utils.list_of_dicts_to_dict_of_lists(results)


#
# # fei platforms
#

if typing.TYPE_CHECKING:
    T = typing.TypeVar('T', int, float)


def fei_deposits_to_deployments(deposit_balances: dict[str, T]) -> dict[str, T]:

    deployment_balances: dict[str, T] = {}
    for deposit, value in deposit_balances.items():

        if deposit in coracle_spec.deposit_metadata:
            deployment = coracle_spec.deposit_metadata[deposit]['platform']
        else:
            deployment = 'Other'

        deployment_balances.setdefault(deployment, type(value)())
        deployment_balances[deployment] += value

    return deployment_balances


def fei_deposits_to_deployments_by_block(
    deposit_balances_by_block: dict[str, list[T]]
) -> dict[str, list[T]]:

    deployment_balances_by_block: dict[str, list[T]] = {}

    for deposit, value in deposit_balances_by_block.items():

        if deposit in coracle_spec.deposit_metadata:
            deployment = coracle_spec.deposit_metadata[deposit]['platform']
        else:
            deployment = 'Other'

        n_blocks = len(value)
        empty = [type(value[i])() for i in range(n_blocks)]
        deployment_balances_by_block.setdefault(deployment, empty)
        deployment_balances_by_block[deployment] = [
            lhs + rhs
            for lhs, rhs in zip(value, deployment_balances_by_block[deployment])
        ]

    return deployment_balances_by_block
