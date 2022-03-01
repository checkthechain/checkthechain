from __future__ import annotations

import asyncio
import typing

import aiohttp

from . import fourbyte_spec


async def async_scrape_function_signatures(
    wait_time: typing.Optional[int] = None,
    print_every: typing.Optional[int] = 10000,
    min_id: typing.Optional[int] = None,
) -> list[fourbyte_spec.Entry]:

    return await async_scrape_set(
        url=fourbyte_spec.endpoints['functions'],
        wait_time=wait_time,
        print_every=print_every,
        min_id=min_id,
    )


async def async_scrape_event_signatures(
    wait_time: typing.Optional[int] = None,
    print_every: typing.Optional[int] = 10000,
    min_id: typing.Optional[int] = None,
) -> list[fourbyte_spec.Entry]:

    return await async_scrape_set(
        url=fourbyte_spec.endpoints['events'],
        wait_time=wait_time,
        print_every=print_every,
        min_id=min_id,
    )


async def async_scrape_set(
    url: str,
    wait_time: typing.Optional[int] = None,
    print_every: typing.Optional[int] = 10000,
    min_id: typing.Optional[int] = None,
) -> list[fourbyte_spec.Entry]:

    results = []

    next_print = None
    if print_every is not None:
        next_print = print_every

    async with aiohttp.ClientSession() as session:
        while True:

            # get page
            async with session.get(url) as response_object:
                response = await response_object.json()
                results.extend(response['results'])

            # scrape only until min_id is reached
            if min_id is not None:
                min_result_id = min(
                    result['id'] for result in response['results']
                )
                if min_result_id < min_id:
                    break

            # get next url
            url = response['next']
            if url is None:
                break

            # print verbose message
            if print_every is not None and next_print is not None:
                if len(results) > next_print:
                    while next_print < len(results):
                        print('scraped', next_print, 'results')
                        next_print += print_every

            # wait between responses
            if wait_time is not None:
                asyncio.sleep(wait_time)

    return results

