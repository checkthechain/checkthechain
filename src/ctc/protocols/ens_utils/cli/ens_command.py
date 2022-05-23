from __future__ import annotations

import toolcli
import toolstr
import tooltime

from ctc import binary
from ctc import evm
from ctc import spec

from ctc.protocols import ens_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_ens_command,
        'help': 'summarize ENS entry',
        'args': [
            {
                'name': 'name_or_address',
                'nargs': '+',
                'help': 'name or address of ENS entry',
            },
            {'name': '--block', 'help': 'block number'},
        ],
    }


async def async_ens_command(
    name_or_address: str,
    block: spec.BlockNumberReference,
) -> None:
    arg = name_or_address[0]

    if block is not None:
        block = binary.standardize_block_number(block)

    if '.' in arg:
        name = arg
        address = await ens_utils.async_resolve_name(name, block=block)
    elif evm.is_address_str(arg):
        address = arg
        name = await ens_utils.async_reverse_lookup(address, block=block)
    else:
        raise Exception('could not parse inputs')

    owner = await ens_utils.async_get_owner(name=name)
    expiration = await ens_utils.async_get_expiration(name=name)
    resolver = await ens_utils.async_get_resolver(name=name)

    toolstr.print_text_box(name)
    print('- address:', address)
    print('- owner:', owner)
    print('- resolver:', resolver)
    print('- namehash:', ens_utils.hash_name(name))
    # print('- registered:', )
    print(
        '- expiration:', tooltime.timestamp_to_iso(expiration).replace('T', ' ')
    )

    text_records = await ens_utils.async_get_text_records(name=name)
    if len(text_records) > 0:
        print()
        print()
        toolstr.print_header('Text Records')
        for key, value in sorted(text_records.items()):
            print('-', key + ':', value)
    else:
        print('- no text records')
