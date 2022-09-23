from __future__ import annotations

import typing

from . import fourbyte_db
from . import fourbyte_spec


#
# # database population functions
#


async def async_build_function_signatures_dataset(
    signature_data: typing.Sequence[fourbyte_spec.PartialEntry]
    | typing.Sequence[fourbyte_spec.Entry]
    | None = None,
) -> None:

    if signature_data is None:
        # TODO: smarter detection of what is currently in database
        print('building function signatures db from scratch, may take awhile')
        signature_data = await async_scrape_function_signatures()

    await fourbyte_db.async_intake_function_signatures(
        function_signatures=signature_data
    )


async def async_build_event_signatures_dataset(
    signature_data: typing.Sequence[fourbyte_spec.PartialEntry]
    | typing.Sequence[fourbyte_spec.Entry]
    | None = None,
) -> None:

    if signature_data is None:
        # TODO: smarter detection of what is currently in database
        print('building event signatures db from scratch, may take awhile')
        signature_data = await async_scrape_event_signatures()

    await fourbyte_db.async_intake_event_signatures(
        event_signatures=signature_data
    )


#
# # entry scraping functions
#


async def async_scrape_function_signatures(
    *,
    wait_time: typing.Optional[int] = None,
    print_every: typing.Optional[int] = 10000,
    min_id: typing.Optional[int] = None,
) -> typing.Sequence[fourbyte_spec.Entry]:

    return await async_scrape_set(
        url=fourbyte_spec.endpoints['functions'],
        wait_time=wait_time,
        print_every=print_every,
        min_id=min_id,
    )


async def async_scrape_event_signatures(
    *,
    wait_time: typing.Optional[int] = None,
    print_every: typing.Optional[int] = 10000,
    min_id: typing.Optional[int] = None,
) -> typing.Sequence[fourbyte_spec.Entry]:

    return await async_scrape_set(
        url=fourbyte_spec.endpoints['events'],
        wait_time=wait_time,
        print_every=print_every,
        min_id=min_id,
    )


async def async_scrape_set(
    url: str,
    *,
    wait_time: typing.Optional[int] = None,
    print_every: typing.Optional[int] = 10000,
    min_id: typing.Optional[int] = None,
) -> typing.Sequence[fourbyte_spec.Entry]:

    import aiohttp

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
                import asyncio

                await asyncio.sleep(wait_time)

    return results
