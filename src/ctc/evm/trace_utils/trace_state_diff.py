from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import toolcli

from ctc import spec
from . import trace_crud


async def async_print_transaction_balance_diffs(
    transaction_hash: spec.TransactionHash,
    *,
    normalize: bool = True,
    include_unchanged: bool = False,
    styles: toolcli.StyleTheme | None = None,
    context: spec.Context = None,
) -> None:
    """print balance of a transaction"""
    import toolstr

    if styles is None:
        styles = {}
    toolstr.print_text_box('ETH Balance Diffs', style=styles.get('title'))
    state_diff = await trace_crud.async_get_transaction_state_diff(
        transaction_hash,
        context=context,
    )
    _print_balance_storage_diffs(
        state_diff,
        include_unchanged=include_unchanged,
        normalize=normalize,
        styles=styles,
    )


async def async_print_transaction_storage_diffs(
    transaction_hash: spec.TransactionHash,
    *,
    styles: toolcli.StyleTheme | None = None,
    context: spec.Context = None,
) -> None:
    """print storage diffs of a transaction"""
    import toolstr

    if styles is None:
        styles = {}
    toolstr.print_text_box('Storage Diffs', style=styles['title'])
    state_diff = await trace_crud.async_get_transaction_state_diff(
        transaction_hash,
        context=context,
    )
    _print_storage_diffs(state_diff, styles=styles)


def _print_balance_storage_diffs(
    state_diff: spec.StateDiffTrace,
    *,
    normalize: bool = True,
    include_unchanged: bool = False,
    styles: toolcli.StyleTheme,
) -> None:

    import toolstr

    rows = []
    for address in state_diff.keys():
        row: list[typing.Any] = [address]
        balance = state_diff[address]['balance']
        if isinstance(balance, str) and balance == '=':
            row.extend([None, None, 0])
        elif isinstance(balance, dict):
            if '+' in balance:
                row.extend([0, balance['+'], balance['+']])  # type: ignore
            elif '*' in balance:
                row.extend(
                    [
                        balance['*']['from'],  # type: ignore
                        balance['*']['to'],  # type: ignore
                        balance['*']['to'] - balance['*']['from'],  # type: ignore
                    ]
                )
            elif '-' in balance:
                row.extend([balance['-'], 0, -balance['-']])
            else:
                raise Exception('unknown balance format')
        else:
            raise Exception('unknown balance format')

        if include_unchanged or row[-1] != 0:
            rows.append(row)

    if normalize:
        for row in rows:
            for i in range(1, 4):
                if isinstance(row[i], int):
                    row[i] /= 1e18

    labels = ['address', 'old', 'new', 'diff']
    toolstr.print_table(
        rows,
        labels=labels,
        compact=2,
        label_style=styles['title'],
        border=styles['comment'],
        column_formats={'diff': {'signed': True, 'scientific': False}},
        column_styles={
            'address': styles['metavar'],
            'old': styles['description'],
            'new': styles['description'],
            'diff': styles['content'],
        },
    )


def _print_storage_diffs(
    state_diff: spec.StateDiffTrace, *, styles: toolcli.StyleTheme
) -> None:
    import toolstr

    rows: list[typing.Any] = []
    for contract_address in state_diff.keys():
        contract_address_label = _shrink_hex(contract_address)
        for storage_slot, values in state_diff[contract_address][
            'storage'
        ].items():

            storage_slot_label = _shrink_hex(storage_slot)
            if '+' in values:
                value = values['+']  # type: ignore
            elif '*' in values:
                value = values['*']['to']  # type: ignore
            else:
                raise Exception()

            row = [
                contract_address_label,
                storage_slot_label,
                value,
            ]
            rows.append(row)
            contract_address_label = ''

    labels = ['contract', 'slot', 'new value']
    toolstr.print_table(
        rows,
        labels=labels,
        label_justify='left',
        compact=2,
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'contract': styles['metavar'],
            'slot': styles['description'],
            'new value': styles['content'],
        },
    )


def _shrink_hex(
    hex_str: str,
    *,
    start_chars: int = 6,
    end_chars: int = 4,
) -> str:
    return hex_str[:start_chars] + '...' + hex_str[-end_chars:]

