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
            {'name': 'name', 'help': 'name of function or event', 'nargs': '?'},
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
                'name': '--functions',
                'help': 'display function abi\'s only',
                'action': 'store_true',
            },
            {
                'name': '--events',
                'help': 'display event abi\'s only',
                'action': 'store_true',
            },
            {'name': '--name', 'help': 'name of function or event abi'},
            {
                'name': '--search',
                'help': 'query of name of function or event abi',
            },
            {
                'name': '--verbose',
                'help': 'include extra abi data',
                'action': 'store_true',
            },
        ],
        'examples': [
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca',
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca --json',
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca --functions',
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca --functions --json',
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca --name Transfer',
        ],
    }


async def async_abi_command(
    address: spec.Address,
    name: str | None,
    json_pretty: bool,
    json_raw: bool,
    functions: bool,
    events: bool,
    search: str,
    verbose: bool,
) -> None:

    address = await evm.async_resolve_address(address)
    contract_abi = await evm.async_get_contract_abi(contract_address=address)

    # filter by name
    if name is not None:
        contract_abi = [
            item
            for item in contract_abi
            if item.get('name') is not None and name == item['name']
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

        if json_raw:
            as_str = json.dumps(contract_abi)
        else:
            as_str = json.dumps(contract_abi, indent=4, sort_keys=True)
        print(as_str)
    if not json_only and not human_only:
        print()
        print()
    if not json_only:
        evm.print_contract_abi_human_readable(
            contract_abi,
            max_width=os.get_terminal_size().columns,
            verbose=verbose,
        )
