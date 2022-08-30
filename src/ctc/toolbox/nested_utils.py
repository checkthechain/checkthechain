from __future__ import annotations

import typing


if typing.TYPE_CHECKING:
    K = typing.TypeVar('K')
    V = typing.TypeVar('V')


def list_of_dicts_to_dict_of_lists(
    list_of_dicts: list[dict[K, V]],
) -> dict[K, list[V]]:
    """convert list of dicts into dict of lists

    uses union of all keys across all dicts
    - any dicts that have missing values will use a fill value (e.g. 0 for ints)

    # TODO: would be nice if could work with list of TypedDict's
    """

    # gather all keys
    all_keys = {
        each_key: None
        for each_dict in list_of_dicts
        for each_key in each_dict.keys()
    }

    # get dtype for fill value
    found = False
    for each_dict in list_of_dicts:
        for value in each_dict.values():
            dtype = type(value)
            found = True
            break
        if found:
            break

    # initialize lists
    dict_of_lists: dict[K, list[V]] = {}
    for key in all_keys.keys():
        dict_of_lists[key] = []

    # build lists
    for each_dict in list_of_dicts:
        for key in all_keys.keys():
            dict_of_lists[key].append(each_dict.get(key, dtype()))

    return dict_of_lists


def is_equal(
    nested_lhs: typing.Mapping[typing.Any, typing.Any],
    nested_rhs: typing.Mapping[typing.Any, typing.Any],
) -> bool:
    import json

    return json.dumps(nested_lhs, sort_keys=True) == json.dumps(
        nested_rhs, sort_keys=True
    )
