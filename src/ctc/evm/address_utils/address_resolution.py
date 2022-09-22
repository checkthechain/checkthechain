# isinstance(address, str) and len(address) > 4 and address.endswith('.eth'):
from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from ctc import spec

#     N = typing.TypeVar('N')


# def is_ens_name(name: typing.Any) -> bool:
#     return (
#         isinstance(name, str)
#         and len(name) > 4
#         and name.endswith('.eth')
#     )


async def async_resolve_address(
    name_or_address: str,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> str:
    """resolve alternate address formats (i.e. ENS) to standard address str"""

    if not (
        isinstance(name_or_address, str)
        and len(name_or_address) > 4
        and name_or_address.endswith('.eth')
    ):
        return name_or_address

    from ctc.protocols import ens_utils

    result = await ens_utils.async_resolve_name(
        name=name_or_address,
        provider=provider,
        block=block,
    )
    if result is not None:
        return result
    else:
        return name_or_address


async def async_resolve_addresses(
    names_or_addresses: typing.Sequence[str],
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[str]:
    """resolve alternate address formats (i.e. ENS) to standard address strs"""

    to_resolve: list[str] = []
    for item in names_or_addresses:
        if isinstance(item, str) and len(item) > 4 and item.endswith('.eth'):
            to_resolve.append(item)

    if len(to_resolve) == 0:
        return names_or_addresses

    else:

        from ctc.protocols import ens_utils

        results = await ens_utils.async_resolve_names(
            names=to_resolve,
            provider=provider,
            block=block,
        )
        resolved: typing.Mapping[str, str | None] = dict(
            zip(to_resolve, results)
        )

        output: list[str] = []
        for name_or_address in names_or_addresses:
            resolved_name_or_address = resolved.get(name_or_address)
            if resolved_name_or_address is not None:
                output.append(resolved_name_or_address)
            else:
                output.append(name_or_address)

        return output


async def async_resolve_address_by_block(
    name_or_address: str,
    *,
    blocks: typing.Sequence[spec.BlockNumberReference],
    provider: spec.ProviderReference = None,
) -> typing.Sequence[str]:
    """return resolution history of address over multiple blocks"""

    import asyncio

    coroutines = [
        async_resolve_address(
            name_or_address=name_or_address,
            provider=provider,
            block=block,
        )
        for block in blocks
    ]

    results = await asyncio.gather(*coroutines)

    return [
        (result if result is not None else name_or_address)
        for result in results
    ]
