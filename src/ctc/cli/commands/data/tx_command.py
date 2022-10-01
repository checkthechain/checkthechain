from __future__ import annotations

import toolcli

from ctc import evm

def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_transaction_command,
        'help': 'display transaction data, receipt, call data, & logs',
        'args': [
            {'name': 'transaction', 'help': 'hash of transaction'},
            {'name': '--sort', 'help': 'attribute to sort logs by'},
            {
                'name': '--json',
                'help': 'output raw JSON of tx',
                'action': 'store_true',
                'dest': 'as_json',
            },
            {
                'name': '--receipt',
                'help': 'output transaction receipt (only works with --json)',
                'action': 'store_true',
                'dest': 'receipt',
            },
        ],
        'examples': [
            '0xe981fe5c78d11d935a1dc35c579969e65e2dd6bb05ad321ea9670f8b1e203eaf',
            '0xe981fe5c78d11d935a1dc35c579969e65e2dd6bb05ad321ea9670f8b1e203eaf --json',
            '0xe981fe5c78d11d935a1dc35c579969e65e2dd6bb05ad321ea9670f8b1e203eaf --json --receipt',
        ],
    }


async def async_transaction_command(
    *, transaction: str, sort: str, as_json: bool, receipt: bool
) -> None:

    if as_json:
        import json
        import asyncio
        from ctc import rpc

        if receipt:
            receipt_task = asyncio.create_task(
                rpc.async_eth_get_transaction_receipt(
                    transaction_hash=transaction
                )
            )
            receipt_data = await receipt_task
            print(json.dumps(receipt_data, sort_keys=True, indent=4))
            return

        transaction_data = await evm.async_get_transaction(transaction)
        print(json.dumps(transaction_data, sort_keys=True, indent=4))

    else:
        if receipt:
            print('receipt flag only works with --json')
            return
        
        await evm.async_print_transaction_summary(
            transaction_hash=transaction, sort_logs_by=sort
        )
