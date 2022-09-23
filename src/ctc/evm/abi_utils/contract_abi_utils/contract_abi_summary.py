from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from .. import function_abi_utils
from .. import event_abi_utils


def get_contract_abi_by_selectors(
    contract_abi: spec.ContractABI,
) -> typing.Mapping[str, spec.ContractABIEntry]:
    """return a mapping from function/event selectors to function/event abis

    omits constructor, receive, and fallback functions
    """
    by_selectors: typing.MutableMapping[str, spec.ContractABIEntry] = {}
    for item in contract_abi:
        if item['type'] == 'function':
            function_selector = function_abi_utils.get_function_selector(item)
            by_selectors[function_selector] = item
        elif item['type'] == 'event':
            event_hash = event_abi_utils.get_event_hash(item)
            by_selectors[event_hash] = item
        elif item['type'] in ['error', 'constructor', 'receive', 'fallback']:
            pass
        else:
            raise Exception('unknown item type in contract abi')
    return by_selectors


def print_contract_abi(
    contract_abi: spec.ContractABI,
    *,
    max_width: int | None = None,
    verbose: bool | int = False,
    read_write: bool = False,
) -> None:
    """print summary of contract ABI"""

    print_contract_abi_functions(
        contract_abi=contract_abi,
        max_width=max_width,
        verbose=verbose,
        read_write=read_write,
    )
    print()
    print()
    print_contract_abi_events(
        contract_abi=contract_abi,
        max_width=max_width,
        verbose=verbose,
    )


def print_contract_abi_functions(
    contract_abi: spec.ContractABI,
    *,
    max_width: int | None = None,
    verbose: bool | int = False,
    title: str = 'Contract ABI Functions',
    read_write: bool = False,
) -> None:
    """print summary of contract ABI functions"""

    import toolstr
    from ctc import cli

    styles = cli.get_cli_styles()

    if read_write:
        read_color = styles['description']
        write_color = 'white'

    functions = evm.get_function_abis(contract_abi)

    if read_write:
        functions = sorted(
            functions,
            key=function_abi_utils.is_function_read_only,
            reverse=True,
        )

    toolstr.print_text_box(title, style=styles['title'])
    print()
    rows = []
    for i, function in enumerate(functions):

        if len(function['outputs']) == 0:
            output_str = '-'
        else:
            output_str_list = [
                (item['type'] + ' ' + item['name']).strip()
                for item in function['outputs']
            ]
            output_str = ', '.join(output_str_list)
            output_str = output_str.strip()
        output_str = output_str.strip()
        if len(output_str) == 0:
            output_str = '-'

        inputs = function.get('inputs', [])
        if len(inputs) == 0:
            inputs = [{'name': '-', 'type': '-'}]

        name = function['name']
        if read_write:
            if function_abi_utils.is_function_read_only(function):
                # read
                name = toolstr.add_style(name, read_color)
            else:
                # write
                name = toolstr.add_style(name, write_color)

        row = [
            function_abi_utils.get_function_selector(function),
            name,
        ]

        if verbose:
            input_items = []
            for item in function.get('inputs', []):
                item_str = item.get('type', '') + ' ' + item.get('name', '')
                item_str = item_str.strip()
                input_items.append(item_str)
            input_str = '\n'.join(input_items)
            if input_str == '':
                input_str = '-'

            row.append(input_str)
            row.append(output_str)
        else:
            row.append(', '.join(item['type'] for item in inputs))
            row.append(output_str)
        rows.append(row)

    name_column = 'name'
    if read_write:
        name_column += (
            ' ('
            + toolstr.add_style('r', read_color)
            + '/'
            + toolstr.add_style('w', write_color)
            + ')'
        )

    labels = [
        'selector',
        name_column,
        'inputs',
        'outputs',
    ]
    if verbose:
        max_column_widths: typing.Mapping[int | str, int] | None = None
    else:
        max_column_widths = {'inputs': 25, 'outputs': 25}

    if verbose:
        toolstr.print_multiline_table(
            rows,
            add_row_index=True,
            labels=labels,
            max_column_widths=max_column_widths,
            compact=4,
            max_table_width=max_width,
            border=styles['comment'],
            label_style=styles['title'],
            column_styles={
                'selector': styles['metavar'],
                'inputs': styles['option'],
                'outputs': styles['option'],
            },
        )
    else:
        toolstr.print_table(
            rows,
            add_row_index=True,
            labels=labels,
            max_column_widths=max_column_widths,
            max_table_width=max_width,
            border=styles['comment'],
            label_style=styles['title'],
            column_styles={
                'selector': styles['metavar'],
                'inputs': styles['option'],
                'outputs': styles['option'],
            },
        )

    print()
    has_constructor = any(
        item['type'] == 'constructor' for item in contract_abi
    )
    has_receive = any(item['type'] == 'receive' for item in contract_abi)
    has_fallback = any(item['type'] == 'fallback' for item in contract_abi)

    print()
    toolstr.print_text_box('Special Functions Present', style=styles['title'])
    print()
    special_rows = [
        ('constructor', has_constructor),
        ('receive', has_receive),
        ('fallback', has_fallback),
    ]
    toolstr.print_table(
        special_rows,
        labels=['function', 'present'],
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'function': styles['option'],
            'present': styles['description'],
        },
        # indent=4,
    )


def print_contract_abi_events(
    contract_abi: spec.ContractABI,
    *,
    max_width: int | None = None,
    verbose: bool | int = False,
    title: str = 'Contract ABI Events',
) -> None:
    """print summary of contract ABI events"""

    import toolstr
    from ctc import cli

    styles = cli.get_cli_styles()

    events = evm.get_event_abis(contract_abi)
    toolstr.print_text_box(title, style=styles['title'])
    print()
    rows = []

    for i, event_abi in enumerate(events):

        name = event_abi['name']
        row = [name]
        input_cell = []
        indexed_cell = []
        for item in event_abi.get('inputs', []):
            subitems = [item.get('type'), item.get('name')]
            subitems_str = [
                subitem for subitem in subitems if subitem is not None
            ]
            input_str = ' '.join(subitems_str)
            input_cell.append(input_str)
            if item.get('indexed'):
                indexed_cell.append('✓')
            else:
                indexed_cell.append('')
        row.append('\n'.join(input_cell))
        row.append('\n'.join(indexed_cell))

        event_hash = event_abi_utils.get_event_hash(event_abi)
        if verbose:
            row.append(event_hash)
        else:
            row.append(event_hash[:6] + '...' + event_hash[-4:])

        rows.append(row)
    labels = ['name', 'inputs', 'indexed', 'event_hash']

    toolstr.print_multiline_table(
        rows,
        add_row_index=True,
        missing_columns='fill',
        labels=labels,
        vertical_justify='top',
        compact=4,
        column_justify={'indexed': 'center'},
        max_table_width=max_width,
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'event_hash': styles['metavar'],
            'inputs': styles['option'],
            'name': styles['description'],
            'indexed': styles['description'],
        },
    )


def contract_abi_to_dataframe(
    contract_abi: spec.ContractABI,
    human_readable: bool,
) -> spec.DataFrame:
    """create pandas DataFrame representation of contract ABI"""

    import copy

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
