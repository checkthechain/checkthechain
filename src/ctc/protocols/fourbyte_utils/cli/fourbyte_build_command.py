from __future__ import annotations

import toolcli

from ctc.protocols import fourbyte_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_fourbyte_build_command,
        'help': 'build local copy of 4byte database\n\nscrapes from 4byte.directory',
        'args': [
            {
                'name': 'datatype',
                'choices': ['functions', 'events'],
                'nargs': '?',
                'help': '"functions" or "events", omit to build database of both',
            },
        ],
        'examples': {
            'functions': {
                'description': 'build function signature db',
                'long': True,
            },
            'events': {'description': 'build event signature db', 'long': True},
        },
    }


async def async_fourbyte_build_command(datatype: str | None) -> None:
    if datatype is None:
        datatypes = ['functions', 'events']
    else:
        datatypes = [datatype]

    print('Building local copy of 4byte database...')

    if 'functions' in datatypes:
        print('Building function signature database...')
        await fourbyte_utils.async_build_function_signatures_dataset()

    if 'events' in datatypes:
        print('Building event signature database...')
        await fourbyte_utils.async_build_event_signatures_dataset()

    print()
    print('local 4byte database up to date')
