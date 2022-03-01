from __future__ import annotations

import typing

from ctc.toolbox import search_utils

from .. import fourbyte_spec
from .. import io_utils


def query_function_signature(
    hex_signature: typing.Optional[str] = None,
    *,
    id: typing.Optional[int] = None,
    bytes_signature: typing.Optional[str] = None,
    text_signature: typing.Optional[str] = None,
) -> list[fourbyte_spec.Entry]:
    if hex_signature is None:
        signatures = io_utils.load_function_signatures()
        signatures_by_hex = None
    else:
        signatures = None
        signatures_by_hex = io_utils.load_function_signatures_by_hex()
    return search_signatures(
        signatures=signatures,
        signatures_by_hex=signatures_by_hex,
        id=id,
        bytes_signature=bytes_signature,
        hex_signature=hex_signature,
        text_signature=text_signature,
    )


def query_event_signature(
    hex_signature: typing.Optional[str] = None,
    *,
    id: typing.Optional[int] = None,
    bytes_signature: typing.Optional[str] = None,
    text_signature: typing.Optional[str] = None,
) -> list[fourbyte_spec.Entry]:
    if hex_signature is None:
        signatures = io_utils.load_event_signatures()
        signatures_by_hex = None
    else:
        signatures = None
        signatures_by_hex = io_utils.load_event_signatures_by_hex()
    return search_signatures(
        signatures=signatures,
        signatures_by_hex=signatures_by_hex,
        id=id,
        bytes_signature=bytes_signature,
        hex_signature=hex_signature,
        text_signature=text_signature,
    )


def search_signatures(
    signatures: typing.Optional[typing.Sequence[fourbyte_spec.Entry]] = None,
    signatures_by_hex: typing.Optional[
        typing.Mapping[str, typing.Sequence[fourbyte_spec.Entry]]
    ] = None,
    id: typing.Optional[int] = None,
    bytes_signature: typing.Optional[str] = None,
    hex_signature: typing.Optional[str] = None,
    text_signature: typing.Optional[str] = None,
) -> list[fourbyte_spec.Entry]:

    inputs = {
        'id': id,
        'bytes_signature': bytes_signature,
        'hex_signature': hex_signature,
        'text_signature': text_signature,
    }
    inputs = {k: v for k, v in inputs.items() if v is not None}

    if hex_signature is not None and signatures_by_hex is not None:

        # append hex prefix
        if not hex_signature.startswith('0x'):
            hex_signature = '0x' + hex_signature

        # query result
        result = signatures_by_hex[hex_signature]

        # assert that other signatures match
        return search_utils.get_matching_entries(
            sequence=result,
            query=inputs,
        )

    else:
        if signatures is None:
            raise Exception(
                'must specify signatures or {hex_signature and signatures_by_hex}'
            )

        inputs = {k: v for k, v in inputs.items() if v is not None}
        return search_utils.get_matching_entries(
            sequence=signatures,
            query=inputs,
        )

