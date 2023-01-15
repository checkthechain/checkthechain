from __future__ import annotations

# see https://ethereum.github.io/beacon-APIs

consensus_endpoints = {
    #
    # beacon
    'beacon_genesis': '/eth/v1/beacon/genesis',
    'beacon_state_root': '/eth/v1/beacon/states/{state_id}/root',
    'beacon_state_fork': '/eth/v1/beacon/states/{state_id}/fork',
    'beacon_finality_checkpoints': '/eth/v1/beacon/states/{state_id}/finality_checkpoints',
    'beacon_validators': '/eth/v1/beacon/states/{state_id}/validators',
    'beacon_validator': '/eth/v1/beacon/states/{state_id}/validators/{validator_id}',
    'beacon_validator_balances': '/eth/v1/beacon/states/{state_id}/validator_balances',
    'beacon_committees': '/eth/v1/beacon/states/{state_id}/committees',
    'beacon_state_sync_committees': '/eth/v1/beacon/states/{state_id}/sync_committees',
    'beacon_blocks_headers': '/eth/v1/beacon/headers',
    'beacon_block_headers': '/eth/v1/beacon/headers/{block_id}',
    'beacon_blocks': '/eth/v1/beacon/blocks',
    'beacon_blinded_blocks': '/eth/v1/beacon/blinded_blocks',
    'beacon_block': '/eth/v2/beacon/blocks/{block_id}',
    'beacon_block_root': '/eth/v1/beacon/blocks/{block_id}/root',
    'beacon_block_attestations': '/eth/v1/beacon/blocks/{block_id}/attestations',
    'beacon_pool_attestations': '/eth/v1/beacon/pool/attestations',
    'beacon_attester_slashings': '/eth/v1/beacon/pool/attester_slashings',
    'beacon_proposer_slashings': '/eth/v1/beacon/pool/proposer_slashings',
    'beacon_pool_sync_committees': '/eth/v1/beacon/pool/sync_committees',
    'beacon_voluntary_exits': '/eth/v1/beacon/pool/voluntary_exits',
    #
    # config
    'config_fork_schedule': '/eth/v1/config/fork_schedule',
    'config_spec': '/eth/v1/config/spec',
    'config_deposit_contract': '/eth/v1/config/deposit_contract',
    #
    # node
    'node_identity': '/eth/v1/node/identity',
    'node_peers': '/eth/v1/node/peers',
    'node_peer': '/eth/v1/node/peers/{peer_id}',
    'node_peer_count': '/eth/v1/node/peer_count',
    'node_version': '/eth/v1/node/version',
    'node_syncing': '/eth/v1/node/syncing',
    'node_health': '/eth/v1/node/health',
}

