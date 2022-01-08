import typing

from ctc import spec

from . import erc20_metadata


async def async_normalize_erc20_quantity(
    quantity: typing.SupportsFloat,
    token: typing.Optional[spec.ERC20Address],
    provider: spec.ProviderSpec = None,
    decimals: typing.Optional[typing.SupportsInt] = None,
    block: spec.BlockNumberReference = 'latest',
) -> float:
    """convert raw erc20 quantity by adjusting radix by (10 ** decimals)"""

    # get decimals
    if decimals is None:
        if token is None:
            raise Exception('must specify token or decimals')
        decimals = await erc20_metadata.async_get_erc20_decimals(
            token, provider=provider, block=block,
        )
    else:
        decimals = int(decimals)

    # normalize
    return float(quantity) / (10 ** decimals)


async def async_normalize_erc20_quantities(
    quantities: typing.Sequence[typing.SupportsInt],
    token: spec.ERC20Address,
    provider: spec.ProviderSpec = None,
    decimals: typing.Optional[typing.SupportsInt] = None,
    block: spec.BlockNumberReference = 'latest',
) -> list[float]:

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
    quantities: typing.Sequence[typing.SupportsInt],
    tokens: typing.Optional[typing.Sequence[spec.ERC20Address]] = None,
    provider: spec.ProviderSpec = None,
    decimals: typing.Optional[typing.Sequence[typing.SupportsInt]] = None,
    block: spec.BlockNumberReference = 'latest',
) -> list[float]:

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

    return [
        quantity / (10 ** decimal)
        for quantity, decimal in zip(quantities, use_decimals)
    ]


async def async_normalize_erc20_quantities_by_block(
    quantities: typing.Sequence[typing.SupportsInt],
    token: typing.Optional[spec.ERC20Address] = None,
    decimals: typing.Optional[list[typing.SupportsInt]] = None,
    provider: spec.ProviderSpec = None,
    blocks: typing.Optional[typing.Iterable[spec.BlockNumberReference]] = None,
) -> list[float]:

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

    return [
        quantity / (10 ** decimal)
        for quantity, decimal in zip(quantities, use_decimals)
    ]


# async def async_normalize_erc20_quantities(
#     quantities: typing.Sequence[typing.SupportsInt],
#     token: typing.Optional[spec.ERC20Address] = None,
#     tokens: typing.Optional[typing.Sequence[spec.ERC20Address]] = None,
#     provider: spec.ProviderSpec = None,
#     decimals: typing.Union[
#         typing.SupportsInt,
#         typing.Sequence[typing.SupportsInt],
#     ] = None,
#     block: typing.Optional[spec.BlockNumberReference] = None,
#     blocks: typing.Optional[typing.Iterable[spec.BlockNumberReference]] = None,
# ) -> list[float]:
#     """convert raw erc20 quantities by adjusting radix by (10 ** decimals)"""

#     n = len(quantities)

#     # parse inputs
#     if token is None and tokens is None:
#         raise Exception('must specify token or tokens')
#     if tokens is not None and len(tokens) != n:
#         raise Exception('number of tokens must match number of quantities')
#     if (
#         decimals is not None
#         and isinstance(decimals, typing.Sequence)
#         and len(decimals) is not None
#     ):
#         raise Exception('number of decimals must match number of quantities')

#     # query decimals if need be
#     if decimals is None:

#         if token is not None:

#             if blocks is not None:
#                 decimals = await erc20_metadata.async_get_erc20_decimals_by_block(
#                     token=token,
#                     provider=provider,
#                     blocks=blocks,
#                 )

#             else:

#                 if block is None:
#                     block = 'latest'
#                 decimals = await erc20_metadata.async_get_erc20_decimals(
#                     token=token,
#                     provider=provider,
#                     block=block,
#                 )

#         elif tokens is not None:

#             if block is None:
#                 block = 'latest'
#             decimals = await erc20_metadata.async_get_erc20s_decimals(
#                 tokens=tokens,
#                 provider=provider,
#                 block=block,
#             )

#         else:
#             raise Exception('must specify token or tokens')

#     # convert decimals to list of int
#     if isinstance(decimals, typing.Iterable):
#         decimals = [int(decimal) for decimal in decimals]
#     elif isinstance(decimals, typing.SupportsInt):
#         decimals = int(decimals)
#         decimals = [decimals for i in range(n)]
#     else:
#         raise Exception('unknown decimals format')
#     decimals = typing.cast(list[int], decimals)

#     # normalize
#     return [
#         quantity / (10 ** decimal)
#         for quantity, decimal in zip(quantities, decimals)
#     ]

