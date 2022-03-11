import tooltable  # type: ignore

from ctc.protocols import fourbyte_utils


def get_command_spec():
    return {
        'f': async_fourbyte_command,
        'help': 'lookup 4byte signature',
        'args': [
            {'name': 'signature', 'help': 'signature to look up'},
            {'name': '--local', 'action': 'store_true', 'help': 'use local database'},
            {'name': '--remote', 'action': 'store_true', 'help': 'use remote database'},
        ],
    }


async def async_fourbyte_command(signature, local, remote):

    try:
        int(signature, 16)
        is_hex = True
    except ValueError:
        is_hex = False

    if local and remote:
        raise Exception('cannot specify both local and remote')
    if local:
        source = 'local'
    elif remote:
        source = 'remote'
    else:
        source = 'remote'

    if is_hex:

        if (signature.startswith('0x') and len(signature) == 10) or len(
            signature
        ) == 8:
            signature_type = 'function'
            results = await fourbyte_utils.async_query_function_signature(
                hex_signature=signature,
                source=source,
            )

        elif (signature.startswith('0x') and len(signature) == 66) or len(
            signature
        ) == 64:
            signature_type = 'event'
            results = await fourbyte_utils.async_query_event_signature(
                hex_signature=signature,
                source=source,
            )

        else:
            raise Exception('could not parse signature: ' + str(signature))

    elif '(' in signature and signature.endswith(')'):

        if signature[0].isupper():
            signature_type = 'event'
            results = await fourbyte_utils.async_query_event_signature(
                text_signature=signature,
                source=source,
            )

        else:
            signature_type = 'function'
            results = await fourbyte_utils.async_query_function_signature(
                text_signature=signature,
                source=source,
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

        headers = [
            'hex',
            'text',
            '4byte id',
        ]

        if len(results) == 1:
            print('1 result')
        else:
            print(len(results), 'results')
        print()
        tooltable.print_table(rows, headers=headers)

    elif signature_type == 'event':
        if len(results) == 0:
            print('[no results]')
        elif len(results) > 1:
            raise Exception('event key collision, this should never happen')
        else:
            result = results[0]
            print(result['text_signature'])
            print('- hash:', result['hex_signature'])
            print('- 4byte id:', result['id'])

