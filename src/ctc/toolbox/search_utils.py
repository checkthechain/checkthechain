from __future__ import annotations

import typing


class NoMatchFound(LookupError):
    pass


class SearchRangeTooLow(NoMatchFound):
    pass


class MultipleMatchesFound(LookupError):
    pass


if typing.TYPE_CHECKING:
    M = typing.TypeVar('M', bound=typing.Mapping[typing.Any, typing.Any])


def get_matching_entries(
    sequence: typing.Sequence[M],
    query: typing.Mapping[typing.Any, typing.Any],
) -> list[M]:
    matches: list[M] = []
    for item in sequence:
        for key, value in query.items():
            if item.get(key) != value:
                break
        else:
            matches.append(item)
    return matches


@typing.overload
def get_matching_entry(
    sequence: typing.Sequence[M],
    query: typing.Mapping[typing.Any, typing.Any],
    *,
    raise_if_not_found: typing.Literal[False],
) -> typing.Optional[M]:
    ...


@typing.overload
def get_matching_entry(
    sequence: typing.Sequence[M],
    query: typing.Mapping[typing.Any, typing.Any],
    *,
    raise_if_not_found: typing.Literal[True] = True,
) -> M:
    ...


def get_matching_entry(
    sequence: typing.Sequence[M],
    query: typing.Mapping[typing.Any, typing.Any],
    *,
    raise_if_not_found: bool = True,
) -> typing.Optional[M]:
    matches = get_matching_entries(sequence=sequence, query=query)
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        raise MultipleMatchesFound('more than one match found in sequence')
    else:
        if raise_if_not_found:
            raise NoMatchFound('no matches found in sequence')
        else:
            return None


def binary_search(
    *,
    is_match: typing.Callable[[int], bool],
    start_index: int | None = None,
    end_index: int | None = None,
    index_range: typing.Sequence[int] | None = None,
    raise_if_not_found: bool = True,
) -> int | None:
    """return the first index for which match returns True"""

    if start_index is None or end_index is None:
        if index_range is None:
            raise Exception(
                'must specify index_range or start_index and end_index'
            )
        start_index, end_index = index_range

    start_index = int(start_index)
    end_index = int(end_index)

    if is_match(start_index):
        return start_index
    if not is_match(end_index):
        if raise_if_not_found:
            raise NoMatchFound('could not find match')
        else:
            return None

    while True:

        midpoint = (start_index + end_index) / 2
        midpoint = int(midpoint)

        if is_match(midpoint):
            end_index = midpoint
        else:
            start_index = midpoint

        if start_index + 1 == end_index:
            return end_index


async def async_binary_search(
    *,
    async_is_match: typing.Callable[
        [int], typing.Coroutine[typing.Any, typing.Any, bool]
    ],
    start_index: int | None = None,
    end_index: int | None = None,
    index_range: typing.Sequence[int] | None = None,
    raise_if_not_found: bool = True,
) -> int | None:
    """return the first index for which match returns True"""

    if start_index is None or end_index is None:
        if index_range is None:
            raise Exception(
                'must specify index_range or start_index and end_index'
            )
        start_index, end_index = index_range

    start_index = int(start_index)
    end_index = int(end_index)

    if await async_is_match(start_index):
        return start_index
    if not await async_is_match(end_index):
        if raise_if_not_found:
            raise NoMatchFound('could not find match')
        else:
            return None

    while True:

        midpoint = (start_index + end_index) / 2
        midpoint = int(midpoint)

        if await async_is_match(midpoint):
            end_index = midpoint
        else:
            start_index = midpoint

        if start_index + 1 == end_index:
            return end_index


def nary_search(
    *,
    nary: int,
    start_index: int,
    end_index: int,
    is_match: typing.Callable[[typing.Sequence[int]], typing.Sequence[bool]],
    debug: bool = False,
    raise_if_not_found: bool = True,
    get_next_probes: typing.Callable[..., typing.Sequence[int]] | None = None,
) -> int | None:

    if get_next_probes is None:
        get_next_probes = get_next_probes_linear

    extra_probes = [start_index, end_index]
    probe_min = start_index
    probe_max = end_index

    while True:

        # if probe range minimized, return result
        if probe_max == probe_min + 1:
            return probe_max

        # get next probes to test
        probes = get_next_probes(
            probe_min=probe_min, probe_max=probe_max, nary=nary
        )
        probes = sorted(set(probes))
        n_probes = len(probes)

        # add in extra probes for start_index and end_index
        all_probes = probes + extra_probes

        # compute results
        all_results = is_match(all_probes)
        results = all_results[:n_probes]
        extra_results = all_results[n_probes:]

        # separate start_index and end_index probes
        if len(extra_probes) > 0:
            start_result, end_result = extra_results
            if start_result:
                return start_index
            elif not end_result:
                if raise_if_not_found:
                    raise Exception('search range does not go high enough')
                else:
                    return None
            extra_probes = []

        # determine lowest successful probe
        for p in range(len(probes)):
            if results[p]:
                break
        else:
            p += 1

        # print state
        if debug:
            print('probe_min:', probe_min)
            print('probe_max:', probe_max)
            print('n_probes:', n_probes)
            print('probes:', probes)
            print('results:', results)
            print('p:', p)
            print()

        # adjust search boundaries
        if p == 0:
            probe_min = probe_min
            probe_max = probes[0]
        elif p == len(probes):
            probe_min = probes[-1]
            probe_max = probe_max
        else:
            probe_min = probes[p - 1]
            probe_max = probes[p]


async def async_nary_search(
    *,
    nary: int,
    start_index: int,
    end_index: int,
    async_is_match: typing.Callable[
        [typing.Sequence[int]],
        typing.Coroutine[typing.Any, typing.Any, typing.Sequence[bool]],
    ],
    debug: bool = False,
    raise_if_not_found: bool = True,
    get_next_probes: typing.Callable[..., typing.Sequence[int]] | None = None,
) -> int | None:

    if get_next_probes is None:
        get_next_probes = get_next_probes_linear

    extra_probes = [start_index, end_index]
    probe_min = start_index
    probe_max = end_index

    while True:

        # if probe range minimized, return result
        if probe_max == probe_min + 1:
            return probe_max

        # get next probes to test
        probes = get_next_probes(
            probe_min=probe_min, probe_max=probe_max, nary=nary
        )
        probes = sorted(set(probes))
        n_probes = len(probes)

        # add in extra probes for start_index and end_index
        all_probes = probes + extra_probes

        # compute results
        all_results = await async_is_match(all_probes)
        results = all_results[:n_probes]
        extra_results = all_results[n_probes:]

        # separate start_index and end_index probes
        if len(extra_probes) > 0:
            start_result, end_result = extra_results
            if start_result:
                return start_index
            elif not end_result:
                if raise_if_not_found:
                    raise SearchRangeTooLow(
                        'search range does not go high enough'
                    )
                else:
                    return None
            extra_probes = []

        # determine lowest successful probe
        for p in range(len(probes)):
            if results[p]:
                break
        else:
            p += 1

        # print state
        if debug:
            print('probe_min:', probe_min)
            print('probe_max:', probe_max)
            print('n_probes:', n_probes)
            print('probes:', probes)
            print('results:', results)
            print('p:', p)
            print()

        # adjust search boundaries
        if p == 0:
            probe_min = probe_min
            probe_max = probes[0]
        elif p == len(probes):
            probe_min = probes[-1]
            probe_max = probe_max
        else:
            probe_min = probes[p - 1]
            probe_max = probes[p]


def get_next_probes_linear(
    *,
    probe_min: int,
    probe_max: int,
    nary: int,
) -> list[int]:
    n_probes = min(nary - 1, probe_max - probe_min - 1)
    d = (probe_max - probe_min) / (n_probes + 1)
    probes = [probe_min + (p + 1) * d for p in range(n_probes)]
    return [round(probe) for probe in probes]
