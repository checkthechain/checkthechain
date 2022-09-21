from __future__ import annotations

import typing

from ctc import spec

from . import erc20_metadata


async def async_normalize_erc20_quantity(
    quantity: typing.SupportsFloat,
    token: typing.Optional[spec.ERC20Address] = None,
    *,
    provider: spec.ProviderReference = None,
    decimals: typing.Optional[typing.SupportsInt] = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> float:
    """convert raw erc20 quantity by adjusting radix by (10 ** decimals)"""

    if quantity == 0:
        return 0

    # get decimals
    if decimals is None:
        if token is None:
            raise Exception('must specify token or decimals')
        decimals_value: int = await erc20_metadata.async_get_erc20_decimals(
            token,
            provider=provider,
            block=block,
        )
    else:
        decimals_value = int(decimals)

    # normalize
    return float(quantity) / int(10 ** decimals_value)


async def async_normalize_erc20_quantities(
    quantities: typing.Sequence[typing.SupportsInt] | spec.Series,
    token: spec.ERC20Address | None = None,
    *,
    provider: spec.ProviderReference = None,
    decimals: typing.Optional[typing.SupportsInt] = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> list[float]:
    """normalize ERC20 quantites by adjusting radix by (10 ** decimals)"""

    if all(quantity == 0 for quantity in quantities):
        return [float(0) for quantity in quantities]

    if decimals is None:
        if token is None:
            raise Exception('must specify token or decimals')
        decimals = await erc20_metadata.async_get_erc20_decimals(
            token=token,
            block=block,
            provider=provider,
        )
    else:
        decimals = int(decimals)

    return [quantity / (10 ** decimals) for quantity in quantities]


async def async_normalize_erc20s_quantities(
    quantities: typing.Sequence[typing.SupportsInt] | spec.Series,
    tokens: typing.Optional[typing.Sequence[spec.ERC20Address]] = None,
    *,
    decimals: typing.Optional[typing.Sequence[typing.SupportsInt]] = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderReference = None,
) -> list[float]:
    """normalize ERC20 quantites by adjusting radix by (10 ** decimals)"""

    # take subset of non zero values
    mask = [quantity != 0 for quantity in quantities]
    any_zero = not all(mask)
    if any_zero:
        old_quantities = quantities
        quantities = [
            quantity for quantity, nonzero in zip(quantities, mask) if nonzero
        ]
        if tokens is not None:
            tokens = [token for token, nonzero in zip(tokens, mask) if nonzero]
        if decimals is not None:
            decimals = [
                decimal for decimal, nonzero in zip(decimals, mask) if nonzero
            ]

    if decimals is None:
        if tokens is None:
            raise Exception('must specify tokens or decimals')
        use_decimals = await erc20_metadata.async_get_erc20s_decimals(
            tokens=tokens,
            block=block,
            provider=provider,
        )
    else:
        use_decimals = [int(decimal) for decimal in decimals]

    if len(use_decimals) != len(quantities):
        raise Exception('number of quantities must match number of decimals')

    # put back in zero values
    if any_zero:
        quantities = old_quantities
        new_use_decimals = []
        use_decimals_iterator = iter(use_decimals)
        for nonzero in mask:
            if nonzero:
                new_use_decimals.append(next(use_decimals_iterator))
            else:
                new_use_decimals.append(1)
        use_decimals = new_use_decimals

    return [
        quantity / (10 ** decimal)
        for quantity, decimal in zip(quantities, use_decimals)
    ]


async def async_normalize_erc20_quantities_by_block(
    quantities: typing.Sequence[typing.SupportsInt] | spec.Series,
    blocks: typing.Sequence[spec.BlockNumberReference],
    *,
    token: typing.Optional[spec.ERC20Address] = None,
    decimals: typing.Optional[list[typing.SupportsInt]] = None,
    provider: spec.ProviderReference = None,
) -> list[float]:
    """normalize ERC20 quantites by adjusting radix by (10 ** decimals)"""

    # take subset of non zero values
    mask = [quantity != 0 for quantity in quantities]
    any_zero = not all(mask)
    if any_zero:
        old_quantities = quantities
        quantities = [
            quantity for quantity, nonzero in zip(quantities, mask) if nonzero
        ]
        blocks = [block for block, nonzero in zip(blocks, mask) if nonzero]
        if decimals is not None:
            decimals = [
                decimal for decimal, nonzero in zip(decimals, mask) if nonzero
            ]

    if decimals is None:
        if token is None:
            raise Exception('must specify token or decimals')
        use_decimals = await erc20_metadata.async_get_erc20_decimals_by_block(
            token=token,
            blocks=blocks,
            provider=provider,
        )
    else:
        use_decimals = [int(decimal) for decimal in decimals]

    if len(use_decimals) != len(quantities):
        raise Exception('number of quantities must match number of decimals')

    if any_zero:
        quantities = old_quantities
        new_use_decimals = []
        use_decimals_iterator = iter(use_decimals)
        for nonzero in mask:
            if nonzero:
                new_use_decimals.append(next(use_decimals_iterator))
            else:
                new_use_decimals.append(1)
        use_decimals = new_use_decimals

    return [
        quantity / (10 ** decimal)
        for quantity, decimal in zip(quantities, use_decimals)
    ]
