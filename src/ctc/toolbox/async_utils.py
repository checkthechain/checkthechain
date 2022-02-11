from __future__ import annotations

import asyncio
import concurrent.futures
import functools
import typing
import types

from typing_extensions import ParamSpec
import pandas as pd


T = typing.TypeVar('T')
R = typing.TypeVar('R')

#
# # gathering
#


async def gather_coroutines(
    *coroutines: typing.Coroutine[typing.Any, typing.Any, R]
) -> list[R]:
    """gather without erasing type information"""
    return await asyncio.gather(*coroutines)


async def gather_dict(
    d: typing.Mapping[T, typing.Coroutine[typing.Any, typing.Any, R]]
) -> dict[T, R]:

    tasks = list(d.values())
    results = await asyncio.gather(*tasks)
    return dict(zip(d.keys(), results))


# typing_extensions does not support ParamSpec properly


# P = ParamSpec('P')


# def sync_wrap(f: typing.Callable[P, R]) -> types.FunctionType:
#     """decorator to create synchronous versions of asynchronous functions

#     - see if anyio has the capability for this already

#     - if currently in an eventloop, f should run in that eventloop
#     - if not currently in an eventloop, f should start one
#     """

#     @functools.wraps(f)
#     def new_f(*args: P.args, **kwargs: P.kwrags) -> R:
#         return asyncio.run(f(*args, **kwargs))

#     return new_f


# async def gather_nested(
#     nested: dict[typing.Any, typing.Any],
# ) -> dict[typing.Any, typing.Any]:

#     # compile tasks
#     tasks = {}
#     for key, value in nested.items():
#         if isinstance(value, dict):
#             tasks[key] = gather_nested(value)
#         elif hasattr(value, '__await__'):
#             tasks[key] = value

#     # await results
#     results = await gather_dict(tasks)

#     # compile output
#     output = {}
#     for key, value in nested.items():
#         if key in results:
#             output[key] = results[key]
#         else:
#             output[key] = value

#     return output


##
## # parallelizing
##

# from typing_extensions import ParamSpec
# ParamSpec = ParamSpec('P')
# T = typing.TypeVar('T')


# async def parallelize(
#    arg: str,
#    values: list[typing.Any],
#    function: typing.Callable[P, T],
#    kwargs: P.kwargs,
# ) -> list[T]:
#    coroutines = []
#    for value in values:
#        coroutine = function(**{arg: value}, **kwargs)
#        coroutines.append(coroutine)
#    return await asyncio.gather(*coroutines)


#
# # csv loading
#


# TODO: many possible solutions to speeding up csv reading + asychronousity
# - shared memory
#     - https://stackoverflow.com/questions/7894791/use-numpy-array-in-shared-memory-for-multiprocessing
#     - https://stackoverflow.com/questions/10721915/shared-memory-objects-in-multiprocessing
#     - https://stackoverflow.com/questions/14124588/shared-memory-in-multiprocessing
# - use seek(n) to have different processes read different parts of same file
# - break into more regularly sized files
# - use hdf instead of csv
# - use database instead of csv
# - things to note:
#    - pandas's read_csv is faster than other python csv libs
#    - the bottleneck is cpu after data is loaded, NOT diskio
#    - if crossing process boundary, data transfers will become an issue


async def async_read_csv(path, mode=None, **kwargs):

    if mode is None:
        mode == 'processes'

    if mode == 'processes':
        return await async_read_csv_processes(path, **kwargs)
    if mode == 'threads':
        return await async_read_csv_threads(path, **kwargs)
    elif mode == 'dask':
        return await async_read_csv_dask(path, **kwargs)
    elif mode == 'aiofiles':
        return await async_read_csv_aiofiles(path, **kwargs)
    elif mode == 'anyio':
        return await async_read_csv_anyio(path, **kwargs)
    else:
        raise Exception('unknown mode: ' + str(mode))


async def async_read_csv_processes(path, pool=None):
    loop = asyncio.get_running_loop()

    if pool is None:
        with concurrent.futures.ProcessPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool,
                functools.partial(pd.read_csv, path),
            )
    else:
        return await loop.run_in_executor(
            pool,
            functools.partial(pd.read_csv, path),
        )


async def async_read_csv_threads(path, pool=None):
    loop = asyncio.get_running_loop()

    if pool is None:
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool,
                functools.partial(pd.read_csv, path),
            )
    else:
        return await loop.run_in_executor(
            pool,
            functools.partial(pd.read_csv, path),
        )


async def async_read_csv_dask(path):
    import dask.dataframe as dd  # type: ignore
    import dask.distributed  # type: ignore

    client = await dask.distributed.Client(asynchronous=True)
    g = dd.read_csv(path, dtype='object')
    return await client.compute(g)


async def async_read_csv_aiofiles(path):
    import io
    import aiofiles

    async with aiofiles.open(path, 'r') as f:
        contents = await f.read()
        string_io = io.StringIO(contents)
        # return string_io
        return pd.read_csv(string_io)


async def async_read_csv_anyio(path):
    import anyio.to_process

    return await anyio.to_process.run_sync(pd.read_csv, path)

