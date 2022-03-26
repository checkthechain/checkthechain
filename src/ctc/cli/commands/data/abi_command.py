import json
import os

from ctc import evm
from ctc import rpc


def get_command_spec():
    return {
        'f': async_abi_command,
        'help': 'display abi of contract',
        'args': [
            {'name': 'address', 'help': 'address of contract'},
            {
                'name': '--human',
                'dest': 'human_only',
                'help': 'human readable only, no json',
                'action': 'store_true',
            },
            {
                'name': '--json',
                'dest': 'json_only',
                'help': 'json only, no human readble',
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
        ],
    }


async def async_abi_command(
    address,
    human_only,
    json_only,
    functions,
    events,
    name,
    search,
):
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
    if not human_only:
        as_str = json.dumps(contract_abi, indent=4, sort_keys=True)
        print(as_str)
    if not json_only and not human_only:
        print()
        print()
    if not json_only:
        evm.print_contract_abi_human_readable(
            contract_abi,
            max_width=os.get_terminal_size().columns,
        )

    await rpc.async_close_http_session()

