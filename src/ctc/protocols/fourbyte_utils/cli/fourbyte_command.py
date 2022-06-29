from __future__ import annotations

import typing

import toolcli
import toolstr

from ctc.protocols import fourbyte_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_fourbyte_command,
        'help': 'lookup 4byte signature',
        'args': [
            {'name': 'signature', 'help': 'signature to look up'},
            {
                'name': '--local',
                'action': 'store_true',
                'help': 'use local database',
            },
            {
                'name': '--remote',
                'action': 'store_true',
                'help': 'use remote database',
            },
        ],
        'examples': [
            '0x18160ddd',
            '0xa9059cbb',
            '"totalSupply()"',
            '"transfer(address,uint256)"',
        ],
    }


async def async_fourbyte_command(
    *, signature: str, local: bool, remote: bool
) -> None:

    if not local and not remote:
        local = True
        remote = True

    try:
        int(signature, 16)
        is_hex = True
    except ValueError:
        is_hex = False

    if is_hex:

        if (signature.startswith('0x') and len(signature) == 10) or len(
            signature
        ) == 8:
            signature_type = 'function'
            results = await fourbyte_utils.async_query_function_signatures(
                hex_signature=signature,
                use_local=local,
                use_remote=remote,
            )

        elif (signature.startswith('0x') and len(signature) == 66) or len(
            signature
        ) == 64:
            signature_type = 'event'
            results = await fourbyte_utils.async_query_event_signatures(
                hex_signature=signature,
                use_local=local,
                use_remote=remote,
            )

        else:
            raise Exception('could not parse signature: ' + str(signature))

    elif '(' in signature and signature.endswith(')'):

        if signature[0].isupper():
            signature_type = 'event'
            results = await fourbyte_utils.async_query_event_signatures(
                text_signature=signature,
                use_local=local,
                use_remote=remote,
            )

        else:
            signature_type = 'function'
            results = await fourbyte_utils.async_query_function_signatures(
                text_signature=signature,
                use_local=local,
                use_remote=remote,
            )
    else:
        raise Exception('could not parse signature: ' + str(signature))

    if signature_type == 'function':
        rows = []
        for result in results:

            hex_signature = result['hex_signature']
            if len(hex_signature) > 10:
                hex_signature = hex_signature[:6] + '...' + hex_signature[-4:]
            row = [
                hex_signature,
                result['text_signature'],
                str(result['id']),
            ]
            rows.append(row)

        labels = [
            'hex',
            'text',
            '4byte id',
        ]

        toolstr.print_text_box('4byte query of ' + str(signature))
        if len(results) == 1:
            print('1 result')
        else:
            print(len(results), 'results')
        print()
        toolstr.print_table(rows, labels=labels)

    elif signature_type == 'event':
        if len(results) == 0:
            print('[no results]')
        elif len(results) > 1:
            raise Exception('event key collision, this should never happen')
        else:
            result = results[0]
            toolstr.print_text_box(result['text_signature'])
            print('- hash:', result['hex_signature'])
            print('- 4byte id:', result['id'])

    else:
        raise Exception('unknown signature_type: ' + str(signature_type))
