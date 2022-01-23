import math

from ctc import evm
from ctc import rpc
from ctc import directory

from . import irm_metadata
from . import pool_metadata
from . import pool_state
from . import token_metadata
from . import token_state


async def async_get_pool_summary(comptroller, block='latest'):

    # get block number
    if block == 'latest':
        block = await rpc.async_eth_block_number()

    # get pool data
    ctokens = await pool_metadata.async_get_pool_ctokens(
        comptroller, block=block
    )
    underlyings = await pool_metadata.async_get_pool_underlying_tokens(
        ctokens=ctokens, block=block
    )
    token_names = []
    for underlying in underlyings.values():
        if underlying == '0x0000000000000000000000000000000000000000':
            token_name = 'ETH'
        elif directory.has_erc20_metadata(address=underlying):
            token_name = directory.get_erc20_symbol(address=underlying)
        else:
            token_name = await evm.async_get_erc20_symbol(underlying)
        token_names.append(token_name)

    # get pricing data
    token_prices = await pool_state.async_get_pool_prices(
        ctokens=ctokens, comptroller=comptroller, block=block
    )

    tokens_data = {}
    blocks_per_year = None
    for ctoken, underlying, token_name in zip(
        ctokens, underlyings, token_names
    ):

        # get blocks per year
        if blocks_per_year is None:
            interest_rate_model = (
                await token_metadata.async_get_ctoken_irm(
                    ctoken=ctoken,
                    block=block,
                )
            )
            blocks_per_year = await irm_metadata.async_get_irm_blocks_per_year(
                interest_rate_model=interest_rate_model,
                block=block,
            )

        # get ctoken stats
        borrowed = await token_state.async_get_total_borrowed(
            ctoken=ctoken, block=block
        )
        borrowed /= 1e18
        liquidity = await token_state.async_get_total_liquidity(
            ctoken=ctoken, block=block
        )
        liquidity /= 1e18
        supply_apy = await token_state.async_get_supply_apy(
            ctoken=ctoken,
            block=block,
            blocks_per_year=blocks_per_year,
        )
        borrow_apy = await token_state.async_get_borrow_apy(
            ctoken=ctoken,
            block=block,
            blocks_per_year=blocks_per_year,
        )

        # compute derived stats
        supplied = borrowed + liquidity
        if math.isclose(supplied, 0):
            utilization = 0
        else:
            utilization = borrowed / supplied

        tokens_data[token_name] = {
            'name': token_name,
            'borrowed': borrowed,
            'borrowed_tvl': borrowed * token_prices[ctoken],
            'supplied': supplied,
            'supplied_tvl': supplied * token_prices[ctoken],
            'liquidity': liquidity,
            'liquidity_tvl': liquidity * token_prices[ctoken],
            'utilization': utilization,
            'borrow_apy': borrow_apy,
            'supply_apy': supply_apy,
        }

    return tokens_data

