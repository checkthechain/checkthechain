from __future__ import annotations

import asyncio
import typing

import toolstr

from ctc import cli
from ctc import evm
from ctc import spec
from . import safe_events
from . import safe_metadata


async def async_print_safe_summary(
    address: spec.Address, verbose: bool = False
) -> None:
    import tooltime

    owners_coroutine = safe_metadata.async_get_safe_owners(address)
    threshold_coroutine = safe_metadata.async_get_safe_threshold(address)
    nonce_coroutine = safe_metadata.async_get_safe_nonce(address)
    creation_block_coroutine = evm.async_get_contract_creation_block(address)

    owners, threshold, nonce, creation_block = await asyncio.gather(
        owners_coroutine,
        threshold_coroutine,
        nonce_coroutine,
        creation_block_coroutine,
    )

    if creation_block is not None:
        creation_timestamp = await evm.async_get_block_timestamp(creation_block)
        creation_date = tooltime.timestamp_to_iso_pretty(creation_timestamp)
        age = tooltime.get_age(creation_timestamp, 'TimelengthPhrase')
    else:
        creation_timestamp = None
        creation_date = None
        age = None

    styles = cli.get_cli_styles()

    toolstr.print_text_box('Gnosis safe ' + str(address), style=styles['title'])
    cli.print_bullet(
        key='threshold',
        value=str(threshold)
        + toolstr.add_style(' / ', styles['comment'])
        + str(len(owners)),
    )
    cli.print_bullet(key='owners', value='')
    for owner in owners:
        cli.print_bullet(value=owner, indent=4)
    cli.print_bullet(key='nonce', value=nonce)
    cli.print_bullet(key='creation block', value=creation_block)
    cli.print_bullet(key='creation date', value=creation_date)
    cli.print_bullet(key='age', value=age)

    if verbose:
        print()
        print()
        await async_print_safe_executions(address)
        print()
        print()
        await async_print_safe_owner_history(address)
        print()
        print()
        await async_print_safe_erc20s(address)


async def async_print_safe_erc20s(address: spec.Address) -> None:

    styles = cli.get_cli_styles()

    default_erc20s = await evm.async_get_default_erc20_tokens()
    erc20_addresses = [default['address'] for default in default_erc20s]

    toolstr.print_text_box('Common ERC20s in safe', style=styles['title'])
    balances = await evm.async_get_erc20s_balances(
        wallet=address,
        tokens=erc20_addresses,
    )

    rows = []
    for erc20, balance in zip(default_erc20s, balances):
        if balance > 0:
            row = [erc20['symbol'], balance]
            rows.append(row)
    labels = ['token', 'balance']
    if len(rows) == 0:
        print('[none]')
    else:
        print()
        toolstr.print_table(
            rows,
            labels=labels,
            indent=4,
            border=styles['comment'],
            label_style=styles['title'],
            column_styles={
                'token': styles['option'],
                'balance': styles['description'],
            },
        )


async def async_print_safe_executions(address: spec.Address) -> None:

    executions = await safe_events.async_get_safe_executions(address)

    # # TODO: output more data about each transaction
    # transaction_hashes = list(executions['transaction_hash'].unique())
    # transactions = await evm.async_get_transactions(transaction_hashes)

    styles = cli.get_cli_styles()

    labels = [
        'nonce',
        'block',
        #     'timestamp',
        #     'age',
        'transaction',
        #     'safeTransaction',
    ]

    rows = []
    for i in range(len(executions)):
        row = [
            i,
            executions.index[i][0],
        ]
        row.append(executions['transaction_hash'].values[i])
        rows.append(row)

    toolstr.print_text_box('Safe Executions', style=styles['title'])
    print()
    toolstr.print_table(
        rows,
        labels=labels,
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'nonce': styles['option'],
            'block': styles['description'],
            'transaction': styles['metavar'],
        },
        compact=2,
    )


async def async_print_safe_owner_history(
    address: spec.Address, end_block: spec.BlockReference | None = None
) -> None:

    if end_block is None:
        end_block = await evm.async_get_latest_block_number()

    safe_setup_coroutine = safe_events.async_get_safe_setup(address)
    owner_adds_coroutine = safe_events.async_get_safe_owner_adds(
        address, end_block=end_block
    )
    owner_removes_coroutine = safe_events.async_get_safe_owner_removes(
        address, end_block=end_block
    )
    threshold_changes_coroutine = safe_events.async_get_safe_threshold_changes(
        address, end_block=end_block
    )

    safe_setup: typing.Any = await safe_setup_coroutine
    owner_adds = await owner_adds_coroutine
    owner_removes = await owner_removes_coroutine
    threshold_changes = await threshold_changes_coroutine

    changes: typing.Sequence[typing.Any] = (
        list(owner_adds.itertuples())
        + list(owner_removes.itertuples())
        + list(threshold_changes.itertuples())
    )
    changes = sorted(changes, key=lambda change: change.Index)  #  type: ignore

    styles = cli.get_cli_styles()

    if safe_setup is not None:
        blocks = [safe_setup.name[0]]
        owners = [set(safe_setup['arg__owners'])]
        threshold = [safe_setup['arg__threshold']]
    else:
        creation_block_coroutine = evm.async_get_contract_creation_block(
            address
        )
        creation_block = await creation_block_coroutine
        owners_coroutine = safe_metadata.async_get_safe_owners(
            address, block=creation_block
        )
        threshold_coroutine = safe_metadata.async_get_safe_threshold(
            address, block=creation_block
        )
        blocks = [creation_block]
        owners = [set(await owners_coroutine)]
        threshold = [await threshold_coroutine]
    diffs = ['safe initialized']
    for change in changes:
        blocks.append(change.Index[0])
        if change.event_name == 'AddedOwner':
            diffs.append(
                'add owner '
                + toolstr.add_style(change.arg__owner, styles['metavar'])
            )
            new_owners = set(owners[-1])
            new_owners.add(change.arg__owner)
            owners.append(new_owners)
            threshold.append(threshold[-1])
        elif change.event_name == 'RemovedOwner':
            diffs.append(
                'remove owner '
                + toolstr.add_style(change.arg__owner, styles['metavar'])
            )
            new_owners = set(owners[-1])
            new_owners.remove(change.arg__owner)
            owners.append(new_owners)
            threshold.append(threshold[-1])
        elif change.event_name == 'ChangedThreshold':
            diffs.append(
                'change signing threshold to '
                + toolstr.add_style(
                    str(change.arg__threshold), styles['description']
                )
            )
            owners.append(owners[-1])
            threshold.append(change.arg__threshold)
        else:
            raise Exception()

    # convert to rows for printout
    rows = []
    for d, diff in enumerate(diffs):
        row = [
            str(blocks[d]),
            diffs[d],
            str(threshold[d])
            + toolstr.add_style(' / ', styles['comment'])
            + str(len(owners[d])),
        ]
        rows.append(row)
    labels = [
        'block',
        'diff',
        'threshold',
    ]

    toolstr.print_text_box('Safe Permission History', style=styles['title'])
    print()
    toolstr.print_table(
        rows=rows,
        labels=labels,
        compact=4,
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'block': styles['description'],
            'threshold': styles['description'],
        },
    )
