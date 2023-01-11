from __future__ import annotations

from ctc import spec


def convert_rpc_block_to_db_block(
    rpc_block: spec.RPCBlock | spec.DBBlock,
) -> spec.DBBlock:
    """convert a raw block from an rpc request into a standard ctc block"""
    return {
        'number': rpc_block['number'],
        'hash': rpc_block['hash'],
        'timestamp': rpc_block['timestamp'],
        'miner': rpc_block['miner'],
        'extra_data': rpc_block['extra_data'],
        'base_fee_per_gas': rpc_block.get('base_fee_per_gas'),
        'gas_limit': rpc_block['gas_limit'],
        'gas_used': rpc_block['gas_used'],
    }

