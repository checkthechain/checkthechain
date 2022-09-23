from __future__ import annotations

import asyncio
import time
import typing

import aiohttp
import toolstr

from ctc import spec
from . import coingecko_db

if typing.TYPE_CHECKING:
    from typing_extensions import TypedDict

    class CoinGeckoRatelimit(TypedDict):
        lock: asyncio.Lock | None
        last_request_time: float
        rps: float
        enabled: bool


_cg_ratelimit: CoinGeckoRatelimit = {
    'lock': None,
    'last_request_time': 0,
    'rps': 50 / 60,
    'enabled': False,
}


urls = {
    'token_list': 'https://api.coingecko.com/api/v3/coins/list',
    'platform_list': 'https://api.coingecko.com/api/v3/coins/list?include_platform=true',
    'token_info': 'https://api.coingecko.com/api/v3/coins/{token_id}',
    'token_market_chart': 'https://api.coingecko.com/api/v3/coins/{token_id}/market_chart?vs_currency=usd&days={days}',
}


async def _async_sleep_for_cg_ratelimit() -> None:

    sleep_time = (
        _cg_ratelimit['last_request_time']
        + 1 / _cg_ratelimit['rps']
        - time.time()
    )
    if sleep_time > 0:
        print('sleeping for', sleep_time, 'seconds')
        await asyncio.sleep(sleep_time)
    _cg_ratelimit['last_request_time'] = time.time()


#
# # lists of tokens
#


async def async_get_token_list(
    use_db: bool = True, update: bool | None = None
) -> typing.Sequence[coingecko_db.CoingeckoToken]:

    if use_db and not update:
        result = await coingecko_db.async_query_tokens()
        if isinstance(result, list) and len(result) > 0:
            return result

    token_list = await _async_get_token_list_from_server(include_platform=False)
    for item in token_list:
        item['market_cap_rank'] = None

    # update db
    if update is None:
        update = True
    if update:
        print('intaking ' + str(len(token_list)) + ' coingecko tokens')
        await coingecko_db.async_intake_tokens(token_list)

    return token_list


async def _async_get_token_list_from_server(
    include_platform: bool = False,
) -> typing.Sequence[typing.Any]:
    if include_platform:
        url = urls['platform_list']
    else:
        url = urls['token_list']

    lock: asyncio.Lock | None = _cg_ratelimit['lock']
    if lock is None:
        lock = asyncio.Lock()
        _cg_ratelimit['lock'] = lock
    async with lock:
        await _async_sleep_for_cg_ratelimit()

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()  # type: ignore


#
# # token symbol --> token id
#


async def async_get_token_name(query: str, use_db: bool = True) -> str:
    """given a token symbol query top token id"""

    if use_db:
        result = await coingecko_db.async_query_tokens(
            symbol_query=query, name_query=query
        )
        if result is not None and len(result) > 0:

            # check for direct symbol matches
            query = query.lower()
            symbol_matches = [
                result for result in result if result['symbol'].lower() == query
            ]
            if len(symbol_matches) >= 1:
                return symbol_matches[0]['name']

            return result[0]['name']

    raise Exception()
    # return await async_get_token_id_from_server(query)


async def async_get_token_id(query: str, use_db: bool = True) -> str:
    """given a token symbol query top token id"""

    if use_db:
        result = await coingecko_db.async_query_tokens(
            symbol_query=query, name_query=query
        )
        if result is not None and len(result) > 0:

            # check for direct symbol matches
            query = query.lower()
            symbol_matches = [
                result for result in result if result['symbol'].lower() == query
            ]
            if len(symbol_matches) >= 1:
                return symbol_matches[0]['id']

            return result[0]['id']

    return await async_get_token_id_from_server(query)


async def async_get_token_id_from_server(symbol: str) -> str:
    """return first result from server token list"""

    token_ids = await async_get_token_ids_from_server(symbol)

    if len(token_ids) == 0:
        raise Exception('cannot find token_id')
    elif len(token_ids) > 1:
        raise Exception('too many token_ids for symbol')
    else:
        return token_ids[0]


async def async_get_token_ids_from_server(
    symbol: str,
) -> typing.Sequence[str]:
    token_ids_by_symbol = await _async_get_token_ids_by_symbol_from_server()
    token_ids = token_ids_by_symbol.get(symbol.lower(), [])
    return token_ids


async def _async_get_token_ids_by_symbol_from_server() -> typing.Mapping[
    str, typing.Sequence[typing.Any]
]:

    # get token list
    token_list = await _async_get_token_list_from_server()

    # process result
    tokens_by_symbol: typing.MutableMapping[
        str, typing.MutableSequence[typing.Any]
    ] = {}
    for item in token_list:
        tokens_by_symbol.setdefault(item['symbol'], [])
        tokens_by_symbol[item['symbol']].append(item['id'])

    return tokens_by_symbol


#
# # token info
#


async def async_get_token_info(
    *,
    symbol: str | None = None,
    token_id: str | None = None,
) -> typing.Mapping[typing.Any, typing.Any]:
    url_template = urls['token_info']

    if token_id is None:
        if symbol is None:
            raise Exception('must specify token_id or symbol')
        token_id = await async_get_token_id(symbol)

    url = url_template.format(token_id=token_id)

    # lock: asyncio.Lock | None = _cg_ratelimit['lock']
    # if lock is None:
    #     lock = asyncio.Lock()
    #     _cg_ratelimit['lock'] = lock
    # async with lock:
    # await _async_sleep_for_cg_ratelimit()

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()  # type: ignore


async def async_get_market_chart(
    *,
    symbol: str | None = None,
    token_id: str | None = None,
    days: str | int | None = None,
) -> typing.Mapping[typing.Any, typing.Any]:

    if days is None:
        days = 'max'

    if token_id is None:
        if symbol is None:
            raise Exception('must specify token_id or symbol')
        token_id = await async_get_token_id(symbol)

    url_template = urls['token_market_chart']
    url = url_template.format(token_id=token_id, days=str(days))

    # lock: asyncio.Lock | None = _cg_ratelimit['lock']
    # if lock is None:
    #     lock = asyncio.Lock()
    #     _cg_ratelimit['lock'] = lock
    # async with lock:
    # await _async_sleep_for_cg_ratelimit()

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data: typing.Mapping[typing.Any, typing.Any] = await response.json()

    if data.get('status', {}).get('error_code') == 429:
        raise Exception(
            'coingecko ratelimit reached, wait a bit or obtain an API key'
        )

    return data


#
# # data summary
#


async def async_print_token_data_summary(
    *,
    token_id: str | None = None,
    query: str | None = None,
    verbose: bool = False,
    update: bool = False,
    days: int | str | None = None,
) -> None:

    if token_id is None:
        if query is None:
            raise Exception('must specify token_id or query')
        token_id = await async_get_token_id(query)

    token_info_coroutine = asyncio.create_task(
        async_get_token_info(token_id=token_id)
    )
    market_chart_coroutine = asyncio.create_task(
        async_get_market_chart(token_id=token_id, days=days)
    )
    token_info = await token_info_coroutine
    market_chart = await market_chart_coroutine

    market_data = token_info['market_data']
    price = market_data['current_price'].get('usd')
    fdv = market_data['fully_diluted_valuation'].get('usd')
    atl = market_data['atl']['usd']
    ath = market_data['ath']['usd']
    market_cap = market_data['market_cap']['usd']

    dollar_format = {
        'prefix': '$',
        'trailing_zeros': True,
        'decimals': 2,
    }

    rows: typing.MutableSequence[typing.Sequence[typing.Any]] = []
    rows.append(['market cap rank', token_info['market_cap_rank']])
    if price is not None:
        rows.append(['price', toolstr.format(price, **dollar_format)])  # type: ignore
    rows.append(['ATL', toolstr.format(atl, **dollar_format)])  # type: ignore
    rows.append(['ATH', toolstr.format(ath, **dollar_format)])  # type: ignore
    rows.append(['total volume', market_data['total_volume']['usd']])
    rows.append(['market cap', toolstr.format(market_cap, **dollar_format)])  # type: ignore
    if fdv is not None:
        rows.append(['FDV', toolstr.format(fdv, **dollar_format)])  # type: ignore
    rows.append(['circulating supply', market_data['circulating_supply']])
    rows.append(['total supply', market_data['total_supply']])

    from ctc import cli

    styles = cli.get_cli_styles()

    toolstr.print_text_box(
        token_info['name'] + ' Coingecko data', style=styles['title']
    )
    print()
    toolstr.print_header('Statistics', style=styles['title'])
    print()
    toolstr.print_table(
        rows,
        indent=4,
        border=styles['comment'],
        column_styles=[styles['option'], styles['description']],
    )

    platforms = token_info['platforms']
    if (
        verbose
        and len(platforms) > 0
        and not (len(platforms) == 1 and tuple(platforms) == ('',))
    ):
        print()
        print()
        toolstr.print_header('Platforms', style=styles['title'])
        rows = []
        for platform, address in token_info['platforms'].items():
            row: typing.Sequence[typing.Any] = (platform, address)
            rows.append(row)
        toolstr.print_table(
            rows,
            indent=4,
            border=styles['comment'],
            column_styles=[styles['option'], styles['description']],
        )

    print()
    toolstr.print_header('Charts', style=styles['title'])
    prices_times = [datum[0] / 1000 for datum in market_chart['prices']]
    total_volumes_times = [
        datum[0] / 1000 for datum in market_chart['total_volumes']
    ]
    market_caps_times = [
        datum[0] / 1000 for datum in market_chart['market_caps']
    ]
    prices = [datum[1] for datum in market_chart['prices']]
    total_volumes = [datum[1] for datum in market_chart['total_volumes']]
    market_caps = [datum[1] for datum in market_chart['market_caps']]

    plots: typing.Sequence[
        tuple[str, typing.Sequence[float | int], typing.Sequence[float | int]]
    ] = [
        ('Price', prices_times, prices),
        ('Market Cap', market_caps_times, market_caps),
        ('Volume', total_volumes_times, total_volumes),
    ]
    for title, xvals, yvals in plots:
        plot = toolstr.render_line_plot(
            xvals=xvals,
            yvals=yvals,
            n_rows=40,
            n_columns=120,
            line_style=styles['description'],
            chrome_style=styles['comment'],
            tick_label_style=styles['metavar'],
            yaxis_kwargs={'tick_label_format': {'prefix': '$'}},
        )
        print()

        if yvals[0] != 0:
            delta = yvals[-1] / yvals[0] - 1
        else:
            delta = float('inf')
        formatted_delta = toolstr.format(delta, percentage=True, signed=True)
        formatted_delta = '(' + formatted_delta + ')'
        formatted_delta = toolstr.add_style(formatted_delta, styles['comment'])
        toolstr.print(
            toolstr.hjustify(title + ' ' + formatted_delta, 'center', 84)[:80],
            indent=4,
            style=styles['title'],
        )
        toolstr.print(plot, indent=4)
        print()

        if title != plots[-1][0]:
            print()

    if verbose:
        print()
        print()
        toolstr.print_header('Tickers', style=styles['title'])
        rows = []
        for ticker in token_info['tickers'][:20]:
            if 'target_coin_id' in ticker:
                target = ticker['target_coin_id']
            else:
                target = ticker['target']
            row = [
                ticker['market']['name'],
                target,
                toolstr.format(ticker['volume'], **dollar_format),  # type: ignore
            ]
            rows.append(row)
        if len(token_info['tickers']) > 20:
            rows.append(['...', '...', '...'])
        labels = [
            'platform',
            'token',
            'volume',
        ]
        toolstr.print_table(
            rows,
            labels=labels,
            indent=4,
            border=styles['comment'],
            label_style=styles['title'],
            column_styles={'volume': styles['description']},
        )

    updated_time_str = 'metadata updated: ' + token_info['last_updated']
    updated_time_str.replace('T', ' ')
    timespan_str = 'timespan = ' + str(days) + ' days'
    timespan_str = toolstr.hjustify(timespan_str, 'right', 73)
    combined_str = updated_time_str + timespan_str[len(updated_time_str) :]
    toolstr.print(combined_str, style=styles['comment'])


async def async_print_coin_quotient_summary(
    coin1: str,
    coin2: str,
    *,
    days: int | None = None,
) -> None:
    import numpy as np
    from ctc import cli

    chart1 = await async_get_market_chart(symbol=coin1, days=days)
    chart2 = await async_get_market_chart(symbol=coin2, days=days)

    coin1_times, coin1_prices = np.array(chart1['prices']).T
    coin2_times, coin2_prices = np.array(chart2['prices']).T

    coin1_times /= 1000
    coin2_times /= 1000

    coin1_over_coin2_times, coin1_over_coin2_prices = _compute_token_quotient(
        coin1_times=coin1_times,
        coin2_times=coin2_times,
        coin1_prices=coin1_prices,
        coin2_prices=coin2_prices,
    )
    coin2_over_coin1_times, coin2_over_coin1_prices = _compute_token_quotient(
        coin1_times=coin2_times,
        coin2_times=coin1_times,
        coin1_prices=coin2_prices,
        coin2_prices=coin1_prices,
    )

    styles = cli.get_cli_styles()

    toolstr.print(
        toolstr.hjustify(coin1 + ' / ' + coin2, 'center', 70),
        indent=4,
        style=styles['title'],
    )
    plot = toolstr.render_line_plot(
        xvals=coin1_over_coin2_times,  # type: ignore
        yvals=coin1_over_coin2_prices,  # type: ignore
        n_rows=40,
        n_columns=120,
        line_style=styles['description'],
        chrome_style=styles['comment'],
        tick_label_style=styles['metavar'],
    )
    toolstr.print(plot, indent=4)

    print()
    print()
    print()
    toolstr.print(
        toolstr.hjustify(coin2 + ' / ' + coin1, 'center', 70),
        indent=4,
        style=styles['title'],
    )
    plot = toolstr.render_line_plot(
        xvals=coin2_over_coin1_times,  # type: ignore
        yvals=coin2_over_coin1_prices,  # type: ignore
        n_rows=40,
        n_columns=120,
        line_style=styles['description'],
        chrome_style=styles['comment'],
        tick_label_style=styles['metavar'],
    )
    toolstr.print(plot, indent=4)


def _compute_token_quotient(
    *,
    coin1_times: spec.NumpyArray,
    coin2_times: spec.NumpyArray,
    coin1_prices: spec.NumpyArray,
    coin2_prices: spec.NumpyArray,
) -> tuple[spec.NumpyArray, spec.NumpyArray]:
    """returns coin1_prices / coin_prices using simple backlook interpolation"""

    import numpy as np

    indices = np.searchsorted(coin1_times, coin2_times)
    nonzero_mask = (indices != 0) * (indices < len(coin1_times))
    nonzero_indices = indices[nonzero_mask]
    comparison_prices = coin1_prices[nonzero_indices]
    coin1_over_coin2_prices = comparison_prices / coin2_prices[nonzero_mask]
    return coin2_times[nonzero_mask], coin1_over_coin2_prices
