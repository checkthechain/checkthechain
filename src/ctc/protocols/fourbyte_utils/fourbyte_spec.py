from __future__ import annotations

import os
import typing

if typing.TYPE_CHECKING:
    from typing_extensions import TypedDict

    class Entry(TypedDict):
        id: int
        created_at: str
        text_signature: str
        hex_signature: str
        bytes_signature: str

    class PartialEntry(TypedDict, total=False):
        id: int
        created_at: str
        text_signature: str
        hex_signature: str
        bytes_signature: str


root_url = 'https://www.4byte.directory'

endpoints = {
    'functions': root_url + '/api/v1/signatures/',
    'function_id': root_url + '/api/v1/signatures/{id}',
    'function_hex': root_url
    + '/api/v1/signatures/?hex_signature={hex_signature}',
    'function_text': root_url
    + '/api/v1/signatures/?text_signature={text_signature}',
    #
    'events': root_url + '/api/v1/event-signatures/',
    'event_id': root_url + '/api/v1/event-signatures/{id}',
    'event_hex': root_url
    + '/api/v1/event-signatures/?hex_signature={hex_signature}',
    'event_text': root_url
    + '/api/v1/event-signatures/?text_signature={text_signature}',
}


def get_default_path(datatype: str) -> str:
    import ctc.config

    if datatype not in ['function_signatures', 'event_signatures']:
        raise Exception('unknown datatype: ' + str(datatype))

    return os.path.join(
        ctc.config.get_data_dir(),
        '4byte',
        datatype + '.json',
    )

