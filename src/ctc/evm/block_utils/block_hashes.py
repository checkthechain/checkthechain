from __future__ import annotations

from .. import binary_utils
from ctc import spec


def serialize_block(block: spec.Block) -> spec.PrefixHexData:
    """serialize block in preparation for hashing"""

    if block.get('base_fee_per_gas') is not None:
        block_type = 'eip1559'
    else:
        block_type = 'legacy'

    as_list = [
        block['parent_hash'],
        block['sha3_uncles'],
        block['miner'],
        block['state_root'],
        block['transactions_root'],
        block['receipts_root'],
        block['logs_bloom'],
        block['difficulty'],
        block['number'],
        block['gas_limit'],
        block['gas_used'],
        block['timestamp'],
        block['extra_data'],
        block['mix_hash'],
        block['nonce'],
    ]

    if block_type == 'eip1559':
        as_list.append(block['base_fee_per_gas'])

    return binary_utils.rlp_encode(as_list)


def hash_block(block: spec.Block) -> spec.PrefixHexData:
    """compute hash of block"""

    serialized = serialize_block(block)
    return binary_utils.keccak(serialized)
