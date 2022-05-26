from __future__ import annotations

import copy
import typing

from ctc import binary
from ctc import spec

from . import abi_io


#
# # summaries
#


async def async_summarize_contract_abi(
    contract_abi: spec.ContractABI | None = None,
    contract_address: spec.Address | None = None,
) -> None:
    if contract_abi is None:
        if contract_address is None:
            raise Exception('must specify contract_abi or contract_address')
        contract_abi = await abi_io.async_get_contract_abi(
            contract_address=contract_address,
        )
    df = contract_abi_to_dataframe(contract_abi, human_readable=True)
    import IPython  # type: ignore

    IPython.display.display(df)


async def async_summarize_contract_events(
    *,
    contract_abi: spec.ContractABI | None = None,
    events: dict[str, spec.EventABI] | None = None,
) -> None:

    if events is None:
        events = await async_get_contract_events(contract_abi=contract_abi)

    print(len(events), 'events:')
    for event in events.values():
        print('-', event['name'])
        for var in event['inputs']:
            if var['indexed']:
                index = 'topic'
            else:
                index = 'data'
            print('    - ' + var['name'] + ':', var['type'] + ',', index)


async def async_get_contract_events(
    contract_abi: spec.ContractABI | None = None,
    **abi_query: typing.Any,
) -> dict[str, spec.EventABI]:
    """get contract events by hash, as {event_hash: event_abi}"""

    if contract_abi is None:
        contract_abi = await abi_io.async_get_contract_abi(**abi_query)

    return {
        binary.get_event_hash(event_abi=abi_item): abi_item
        for abi_item in contract_abi
        if abi_item['type'] == 'event'
    }


def print_contract_abi_human_readable(
    contract_abi: spec.ContractABI,
    max_width: int = 80,
    verbose: bool | int = False,
) -> None:
    functions = binary.get_function_abis(contract_abi)

    print('Contract ABI Functions')
    print('──────────────────────')
    for i, function in enumerate(functions):

        if len(function['outputs']) == 0:
            output_str = '[none]'
        else:
            output_str_list = [
                item['type'] + ' ' + item['name']
                for item in function['outputs']
            ]
            output_str = ', '.join(output_str_list)
            if len(function['outputs']) > 1:
                output_str = '(' + output_str + ')'

        if not verbose:
            signature = binary.get_function_signature(
                function_abi=function,
                include_names=True,
            )
        else:
            signature = function['name'] + '()'
        if verbose:
            text = signature + ' --> ' + str(output_str)
        else:
            text = str(i + 1) + '. ' + signature + ' --> ' + str(output_str)

        if len(text) > max_width:
            text = text[: max_width - 3] + '...'

        print(text)
        if verbose:
            indent = ''
            if verbose > 1:
                indent = '    '
                print(indent + '- mutability:', function['stateMutability'])
                print(indent + '- inputs:')
            if len(function['inputs']) == 0:
                print(indent + '    [no inputs]')
            for i, item in enumerate(function['inputs']):
                print(
                    indent + '    ' + str(i + 1) + '.',
                    item['type'],
                    item['name'],
                )
            print()

    events = binary.get_event_abis(contract_abi)
    print()
    print('Contract ABI Events')
    print('───────────────────')
    if len(events) == 0:
        print('[none]')
    for i, event_abi in enumerate(events):
        event_hash = binary.get_event_hash(event_abi=event_abi)
        signature = binary.get_event_signature(event_abi=event_abi)
        line = str(i + 1) + '. ' + signature
        if len(line) > max_width:
            line = line[: max_width - 3] + '...'
        print(line)
        if verbose:
            print('  ', event_hash)
            if i + 1 != len(events):
                print()


#
# # dataframes
#


def contract_abi_to_dataframe(
    contract_abi: spec.ContractABI,
    human_readable: bool,
) -> spec.DataFrame:
    contract_abi = copy.deepcopy(contract_abi)
    for entry in typing.cast(
        typing.List[typing.Dict[str, typing.Any]], contract_abi
    ):

        if human_readable:

            if 'name' not in entry:
                entry['name'] = ''

            if 'inputs' in entry:
                inputs = []
                for input in entry['inputs']:
                    input_str = ''
                    input_str += input.get('type', '')
                    input_name = input.get('name', '')
                    if input_name is not None and input_name != '':
                        input_str += ' ' + input_name
                    inputs.append(input_str)
                entry['inputs'] = ', '.join(inputs)
            else:
                entry['inputs'] = ''

            if 'outputs' in entry:
                outputs = []
                for output in entry['outputs']:
                    output_str = ''
                    output_str += output.get('type')
                    output_name = output.get('name')
                    if output_name is not None and output_name != '':
                        output_str += ' ' + output_name
                    outputs.append(output_str)
                entry['outputs'] = ', '.join(outputs)
            else:
                entry['outputs'] = ''

            if 'anonymous' not in entry:
                entry['anonymous'] = ''

            if 'stateMutability' not in entry:
                entry['stateMutability'] = ''

    import pandas as pd

    df = pd.DataFrame(contract_abi)
    df = df.reindex(
        columns=[
            'type',
            'name',
            'inputs',
            'outputs',
            'stateMutability',
            'anonymous',
        ]
    )

    return df


async def async_get_contract_events_dataframe(
    contract_abi: spec.ContractABI,
    contract_name: str | None = None,
    contract_address: spec.Address | None = None,
    protocol_name: str | None = None,
) -> spec.DataFrame:

    event_abis = await async_get_contract_events(contract_abi=contract_abi)
    event_rows = []
    for event_hash, event_abi in event_abis.items():

        data_types = binary.get_event_unindexed_types(event_abi=event_abi)
        data_names = binary.get_event_unindexed_names(event_abi=event_abi)
        data_signature = [
            data_type + ' ' + data_name
            for data_type, data_name in zip(data_types, data_names)
        ]

        event_row = {
            'protocol_name': protocol_name,
            'contract_address': contract_address,
            'contract_name': contract_name,
            'event_name': event_abi['name'],
            'event_hash': event_hash,
            'topic1_type': None,
            'topic1_name': None,
            'topic2_type': None,
            'topic2_name': None,
            'topic3_type': None,
            'topic3_name': None,
            'data_signature': data_signature,
        }

        n_topics = 0
        for var in event_abi['inputs']:
            if var['indexed']:
                n_topics += 1
                event_row['topic' + str(n_topics) + '_type'] = var['type']
                event_row['topic' + str(n_topics) + '_name'] = var['name']

        event_rows.append(event_row)

    import pandas as pd

    return pd.DataFrame(event_rows)
