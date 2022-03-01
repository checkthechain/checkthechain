from __future__ import annotations

import typing

import toolcache

from ctc.toolbox import store_utils

from . import fourbyte_spec


def save_function_signatures(
    signatures: typing.Sequence[fourbyte_spec.Entry],
    path: typing.Optional[str] = None,
    overwrite: bool = False,
    verbose: bool = True,
) -> list[fourbyte_spec.Entry]:

    # get default path
    if path is None:
        path = fourbyte_spec.get_default_path('function_signatures')

    # save
    return save_signatures(
        signatures=signatures,
        path=path,
        overwrite=overwrite,
        verbose=verbose,
    )


def save_event_signatures(
    signatures: typing.Sequence[fourbyte_spec.Entry],
    path: typing.Optional[str] = None,
    overwrite: bool = False,
    verbose: bool = True,
) -> list[fourbyte_spec.Entry]:

    # get default path
    if path is None:
        path = fourbyte_spec.get_default_path('event_signatures')

    # save
    return save_signatures(
        signatures=signatures,
        path=path,
        overwrite=overwrite,
        verbose=verbose,
    )


def save_signatures(
    signatures: typing.Sequence[fourbyte_spec.Entry],
    path: str,
    overwrite: bool = False,
    verbose: bool = True,
) -> list[fourbyte_spec.Entry]:

    # deduplicate and sort
    signatures_by_id = {}
    for signature in signatures:
        if signature['id'] in signatures_by_id:
            pass
        else:
            signatures_by_id[signature['id']] = signature
    signatures = [
        signatures_by_id[key] for key in sorted(signatures_by_id.keys())
    ]

    # output verbosity
    if verbose:
        print('saving', len(signatures), 'signatures to path', path)

    # write data
    store_utils.write_file_data(data=signatures, path=path, overwrite=overwrite)

    return signatures


def load_function_signatures(
    path: typing.Optional[str] = None,
) -> list[fourbyte_spec.Entry]:

    if path is None:
        path = fourbyte_spec.get_default_path('function_signatures')

    return store_utils.load_file_data(path=path)


def load_event_signatures(
    path: typing.Optional[str] = None,
) -> list[fourbyte_spec.Entry]:

    if path is None:
        path = fourbyte_spec.get_default_path('event_signatures')

    return store_utils.load_file_data(path=path)


@toolcache.cache(cachetype='memory')
def load_function_signatures_by_hex() -> dict[str, list[fourbyte_spec.Entry]]:
    signatures = load_function_signatures()
    signatures_by_hex: dict[str, list[fourbyte_spec.Entry]] = {}
    for signature in signatures:
        signatures_by_hex.setdefault(signature['hex_signature'], [])
        signatures_by_hex[signature['hex_signature']].append(signature)
    return signatures_by_hex


@toolcache.cache(cachetype='memory')
def load_event_signatures_by_hex() -> dict[str, list[fourbyte_spec.Entry]]:
    signatures = load_event_signatures()
    signatures_by_hex: dict[str, list[fourbyte_spec.Entry]] = {}
    for signature in signatures:
        signatures_by_hex.setdefault(signature['hex_signature'], [])
        signatures_by_hex[signature['hex_signature']].append(signature)
    return signatures_by_hex

