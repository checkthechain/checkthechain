# isinstance(address, str) and len(address) > 4 and address.endswith('.eth'):
from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from ctc import spec

    N = typing.TypeVar('N')


# def is_ens_name(name: typing.Any) -> bool:
#     return (
#         isinstance(name, str)
#         and len(name) > 4
#         and name.endswith('.eth')
#     )


async def async_resolve_address(
    name_or_address: N,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> N:

    if not (
        isinstance(name_or_address, str)
        and len(name_or_address) > 4
        and name_or_address.endswith('.eth')
    ):
        return name_or_address

    from ctc.protocols import ens_utils

    return await ens_utils.async_resolve_name(  # type: ignore
        name=name_or_address,
        provider=provider,
        block=block,
    )


async def async_resolve_addresses(
    names_or_addresses: typing.Sequence[N],
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[N]:

    to_resolve = {}
    for i, item in enumerate(names_or_addresses):
        if isinstance(item, str) and len(item) > 4 and item.endswith('.eth'):
            to_resolve[i] = item

    if len(to_resolve) == 0:
        return names_or_addresses

    else:

        from ctc.protocols import ens_utils

        results = await ens_utils.async_resolve_names(
            names=list(to_resolve.values()),
            provider=provider,
            block=block,
        )
        resolved = dict(zip(to_resolve.keys(), results))

        return [
            resolved.get(i, item)  # type: ignore
            for i, item in enumerate(names_or_addresses)
        ]


async def async_resolve_address_by_block(
    name_or_address: N,
    *,
    blocks: typing.Sequence[spec.BlockNumberReference],
    provider: spec.ProviderReference = None,
) -> typing.Sequence[N]:
    import asyncio

    coroutines = [
        async_resolve_address(
            name_or_address=name_or_address,
            provider=provider,
            block=block,
        )
        for block in blocks
    ]

    return await asyncio.gather(*coroutines)
