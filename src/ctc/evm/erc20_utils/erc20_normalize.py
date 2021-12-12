import typing

from ctc import spec

from . import erc20_metadata


async def async_normalize_erc20_quantity(
    quantity: typing.SupportsFloat,
    token: spec.TokenReference,
    provider: spec.ProviderSpec = None,
    decimals: typing.Optional[typing.SupportsInt] = None,
    block: spec.BlockNumberReference = 'latest',
) -> float:
    """convert raw erc20 quantity by adjusting radix by (10 ** decimals)"""

    # get decimals
    if decimals is None:
        decimals = await erc20_metadata.async_get_erc20_decimals(
            token, provider=provider, block=block,
        )

    # normalize
    return float(quantity) / (10 ** int(decimals))


async def async_normalize_erc20_quantities(
    quantities: typing.Sequence[typing.SupportsInt],
    token: typing.Optional[spec.TokenReference] = None,
    tokens: typing.Optional[typing.Sequence[spec.TokenReference]] = None,
    provider: spec.ProviderSpec = None,
    decimals: typing.Union[
        typing.SupportsInt,
        typing.Sequence[typing.SupportsInt],
    ] = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
    blocks: typing.Optional[typing.Iterable[spec.BlockNumberReference]] = None,
) -> list[float]:
    """convert raw erc20 quantities by adjusting radix by (10 ** decimals)"""

    n = len(quantities)

    # parse inputs
    if token is None and tokens is None:
        raise Exception('must specify token or tokens')
    if tokens is not None and len(tokens) != n:
        raise Exception('number of tokens must match number of quantities')
    if (
        decimals is not None
        and isinstance(decimals, typing.Sequence)
        and len(decimals) is not None
    ):
        raise Exception('number of decimals must match number of quantities')

    # query decimals if need be
    if decimals is None:

        if token is not None:

            if blocks is not None:
                decimals = await erc20_metadata.async_get_erc20_decimals_by_block(
                    token=token,
                    provider=provider,
                    blocks=blocks,
                )

            else:

                if block is None:
                    block = 'latest'
                decimals = await erc20_metadata.async_get_erc20_decimals(
                    token=token,
                    provider=provider,
                    block=block,
                )

        elif tokens is not None:

            if block is None:
                block = 'latest'
            decimals = await erc20_metadata.async_get_erc20s_decimals(
                tokens=tokens,
                provider=provider,
                block=block,
            )

        else:
            raise Exception('must specify token or tokens')

    # convert decimals to list of int
    if isinstance(decimals, typing.Iterable):
        decimals = [int(decimal) for decimal in decimals]
    elif isinstance(decimals, typing.SupportsInt):
        decimals = int(decimals)
        decimals = [decimals for i in range(n)]
    else:
        raise Exception('unknown decimals format')
    decimals = typing.cast(list[int], decimals)

    # normalize
    return [
        quantity / (10 ** decimal)
        for quantity, decimal in zip(quantities, decimals)
    ]

