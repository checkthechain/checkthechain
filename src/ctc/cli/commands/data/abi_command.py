from __future__ import annotations

import os
import typing

import toolcli

from ctc import evm

if typing.TYPE_CHECKING:
    from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_abi_command,
        'help': 'display abi of contract',
        'args': [
            {'name': 'address', 'help': 'address of contract'},
            {
                'name': 'names',
                'help': 'name of function or event',
                'nargs': '*',
            },
            # {
            #     'name': '--rw',
            #     'help': 'sort function entries by read vs write functions',
            #     'action': 'store_true',
            #     'dest': 'read_write',
            # },
            {
                'name': '--json',
                'dest': 'json_pretty',
                'help': 'json only',
                'action': 'store_true',
            },
            {
                'name': '--json-raw',
                'help': 'json only, without sorting or indentations',
                'action': 'store_true',
            },
            {
                'name': '--map-names',
                'help': 'output ABI as map where names are the keys',
                'action': 'store_true',
            },
            {
                'name': '--map-selectors',
                'help': 'output ABI as map where hash selectors are the keys',
                'action': 'store_true',
            },
            {
                'name': ['-f', '--functions'],
                'help': 'display function abi\'s only',
                'action': 'store_true',
            },
            {
                'name': ['-e', '--events'],
                'help': 'display event abi\'s only',
                'action': 'store_true',
            },
            {
                'name': '--search',
                'help': 'query of name of function or event abi',
            },
            {
                'name': ['--verbose', '-v'],
                'help': 'include extra abi data',
                'action': 'store_true',
            },
            {
                'name': '--python',
                'help': 'output data as pep8-formatted python syntax',
                'action': 'store_true',
            },
            {
                'name': '--update',
                'help': 're-import ABI from etherscan (e.g. if proxy has changed)',
                'action': 'store_true',
            },
        ],
        'examples': [
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca',
            '0x2b79b3c3c7b35463a28a76e0d332aab3e20aa337 Mint Burn Swap Sync',
            '0x2b79b3c3c7b35463a28a76e0d332aab3e20aa337 -f',
            '0x2b79b3c3c7b35463a28a76e0d332aab3e20aa337 -e',
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca --json',
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca --map-names --python',
        ],
    }


async def async_abi_command(
    *,
    address: spec.Address,
    names: typing.Sequence[str],
    # read_write: bool,
    json_pretty: bool,
    json_raw: bool,
    functions: bool,
    events: bool,
    search: str,
    verbose: bool,
    map_names: bool,
    map_selectors: bool,
    python: bool,
    update: bool,
) -> None:

    if map_names and map_selectors:
        raise Exception('can only specify one of --map-names or --map-keys')
    if map_names or map_selectors:
        if not json_raw:
            json_pretty = True

    address = await evm.async_resolve_address(address)
    contract_abi = await evm.async_get_contract_abi(
        contract_address=address, db_query=(not update),
    )

    # filter by name
    if len(names) > 0:
        contract_abi = [
            item
            for item in contract_abi
            if item.get('name') is not None
            and any(name == item['name'] for name in names)
        ]
    if search is not None:
        search = search.lower()
        contract_abi = [
            item
            for item in contract_abi
            if item.get('name') is not None and search in item['name'].lower()
        ]

    # filter by type
    if functions:
        contract_abi = [
            item for item in contract_abi if item.get('type') == 'function'
        ]
    if events:
        contract_abi = [
            item for item in contract_abi if item.get('type') == 'event'
        ]

    # output abis
    json_only = json_pretty or json_raw
    human_only = not json_only
    if not human_only:
        import json

        if map_names:
            json_data: typing.Any = {}
            for item in contract_abi:
                name = item.get('name')
                if name is None:
                    continue
                if name in json_data:
                    raise Exception('ABI naming conflict: ' + str(name))
                json_data[name] = item
        elif map_selectors:
            json_data = evm.get_contract_abi_by_selectors(contract_abi)
        else:
            json_data = contract_abi

        if json_raw:
            as_str = json.dumps(json_data)
        else:
            as_str = json.dumps(json_data, indent=4, sort_keys=True)

        # convert from json to python syntax
        if python:
            import re

            as_str = re.sub('(?<![\[{,])\n', ',\n', as_str)
            as_str = as_str.replace('"', '\'')
            as_str = as_str.replace(': true,\n', ': True,\n')
            as_str = as_str.replace(': false,\n', ': False,\n')

        print(as_str)
    if not json_only and not human_only:
        print()
        print()
    if not json_only:
        columns = toolcli.get_n_terminal_cols()

        if functions:
            evm.print_contract_abi_functions(
                contract_abi,
                max_width=columns,
                verbose=verbose,
                read_write=True,
            )

        elif events:
            evm.print_contract_abi_events(
                contract_abi,
                max_width=columns,
                verbose=verbose,
            )

        else:
            evm.print_contract_abi(
                contract_abi,
                max_width=columns,
                verbose=verbose,
                read_write=True,
            )
