from __future__ import annotations

import typing

from ctc import evm
from ctc import spec

from . import pool_summary


async def async_plot_lbp_summary(
    *,
    swaps: spec.DataFrame,
    weights: spec.DataFrame,
    pool_name: str,
    pool_tokens: typing.Sequence[spec.Address],
    pool_address: spec.Address,
    price_range: typing.Sequence[int | float] | None = None,
    premium_range: typing.Sequence[int | float] | None = None,
    oracle_data: spec.DataFrame | None = None,
) -> None:

    summary = pool_summary.summarize_pool_swaps(swaps=swaps, weights=weights)

    for pair in summary.keys():

        blocks = summary[pair].index.get_level_values('block_number')

        token_0, token_1 = await evm.async_get_erc20s_symbols(pool_tokens)
        in_address, out_address = pair
        if in_address == pool_tokens[0]:
            in_token = token_0
            out_token = token_1
            in_weights = summary[pair]['weight_0']
            out_weights = summary[pair]['weight_1']
        else:
            out_token = token_0
            in_token = token_1
            out_weights = summary[pair]['weight_0']
            in_weights = summary[pair]['weight_1']

        title = pool_name + ', in=' + in_token + ', out=' + out_token

        if oracle_data is not None:
            min_block = swaps.index[0][0]
            max_block = swaps.index[-1][0]
            oracle_mask = (oracle_data.index >= min_block) & (
                oracle_data.index <= max_block
            )
            oracle_data = oracle_data[oracle_mask]
            if oracle_data is None:
                raise Exception('invalid oracle_data')
            ys = [
                {
                    'y': oracle_data.values,
                    'x': oracle_data.index.values,
                    'y_kwargs': {'label': 'oracle'},
                },
            ]

            if oracle_data is None:
                raise Exception('invalid oracle_data')
            premium = []
            for index, row in summary[pair].iterrows():
                block_number = index[0]  # type: ignore
                oracle_price = oracle_data[block_number]
                actual_price = row['price_out_per_in']
                premium.append(float(actual_price) / oracle_price - 1)
        else:
            ys = None
            premium = []

        y_kwargs = {'marker': '.', 'markersize': 10, 'linewidth': 1}
        plot_data = {
            'subplot_height': 5,
            'common': {
                'x': blocks,
                'name_position': 'ylabel',
                'tickgrid': True,
                'y_kwargs': y_kwargs,
            },
            'plots': {
                'price': {
                    'title': title,
                    'name': 'price\n(' + out_token + ' / ' + in_token + ')',
                    'y': summary[pair]['price_out_per_in'],
                    'y_kwargs': dict(label='actual', **y_kwargs),
                    'ys': ys,
                    'ylim': price_range,
                    # 'legend_kwargs': {'loc': 'lower left'},
                },
                'premium': {
                    'name': 'price premium',
                    'y': premium,
                    'ylim': premium_range,
                },
                'weight': {
                    'name': out_token + ' Weights',
                    'y': out_weights,
                },
                'token0 Sold': {
                    'name': in_token + ' Amount',
                    'y': summary[pair]['in_amounts'],
                },
                'Cummulative token0 Bought': {
                    'name': 'Cummulative\n' + in_token + ' Bought',
                    'y': summary[pair]['cummulative_in_amount'],
                },
                'Cummulative token1 Sold': {
                    'name': 'Cummulative\n' + out_token + 'Sold',
                    'y': summary[pair]['cummulative_out_amount'],
                },
                'Volume Weighted Price': {
                    'name': 'Cummulative\nVolume Weighted\nPrice',
                    'y': summary[pair]['cummulative_price_out_per_in'],
                    'xlabel': 'block',
                    'ylim': price_range,
                },
            },
        }

        import toolplot  # type: ignore

        toolplot.plot_subplots(plot_data)
