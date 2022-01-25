from ctc import evm
from ctc import spec

from .. import rpc_provider
from . import rpc_batch_utils


def batch_eth_accounts(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_accounts', **kwargs)


async def async_batch_eth_accounts(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_accounts', **kwargs)


def batch_eth_block_number(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_block_number', **kwargs)


async def async_batch_eth_block_number(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_block_number', **kwargs
    )


def batch_eth_call(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_call', **kwargs)


async def async_batch_eth_call(
    function_abi=None,
    function_name=None,
    function_selector=None,
    provider=None,
    to_address=None,
    to_addresses=None,
    **kwargs,
) -> spec.RpcPluralResponse:

    if function_abi is None:

        if to_address is not None:
            contract_address = to_address
        elif to_addresses is not None:
            contract_address = to_addresses[0]
        else:
            raise Exception(
                'must specify contract_address or contract_addresses'
            )

        provider = rpc_provider.get_provider(provider)
        network = provider['network']
        if network is None:
            raise Exception('could not determine network')

        function_abi = await evm.async_get_function_abi(
            contract_address=contract_address,
            function_name=function_name,
            function_selector=function_selector,
            network=network,
        )

    return await rpc_batch_utils.async_batch_execute(
        'eth_call',
        function_abi=function_abi,
        provider=provider,
        to_address=to_address,
        to_addresses=to_addresses,
        **kwargs,
    )


def batch_eth_coinbase(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_coinbase', **kwargs)


async def async_batch_eth_coinbase(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_coinbase', **kwargs)


def batch_eth_compile_lll(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_compile_lll', **kwargs)


async def async_batch_eth_compile_lll(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_compile_lll', **kwargs
    )


def batch_eth_compile_serpent(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_compile_serpent', **kwargs)


async def async_batch_eth_compile_serpent(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_compile_serpent', **kwargs
    )


def batch_eth_compile_solidity(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_compile_solidity', **kwargs)


async def async_batch_eth_compile_solidity(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_compile_solidity', **kwargs
    )


def batch_eth_estimate_gas(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_estimate_gas', **kwargs)


async def async_batch_eth_estimate_gas(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_estimate_gas', **kwargs
    )


def batch_eth_gas_price(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_gas_price', **kwargs)


async def async_batch_eth_gas_price(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_gas_price', **kwargs)


def batch_eth_get_balance(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_get_balance', **kwargs)


async def async_batch_eth_get_balance(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_balance', **kwargs
    )


def batch_eth_get_block_by_hash(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_get_block_by_hash', **kwargs)


async def async_batch_eth_get_block_by_hash(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_block_by_hash', **kwargs
    )


def batch_eth_get_block_by_number(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_get_block_by_number', **kwargs)


async def async_batch_eth_get_block_by_number(
    **kwargs,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_block_by_number', **kwargs
    )


def batch_eth_get_block_transaction_count_by_hash(
    **kwargs,
) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute(
        'eth_get_block_transaction_count_by_hash', **kwargs
    )


async def async_batch_eth_get_block_transaction_count_by_hash(
    **kwargs,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_block_transaction_count_by_hash', **kwargs
    )


def batch_eth_get_block_transaction_count_by_number(
    **kwargs,
) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute(
        'eth_get_block_transaction_count_by_number', **kwargs
    )


async def async_batch_eth_get_block_transaction_count_by_number(
    **kwargs,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_block_transaction_count_by_number', **kwargs
    )


def batch_eth_get_code(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_get_code', **kwargs)


async def async_batch_eth_get_code(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_get_code', **kwargs)


def batch_eth_get_compilers(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_get_compilers', **kwargs)


async def async_batch_eth_get_compilers(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_compilers', **kwargs
    )


def batch_eth_get_filter_changes(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_get_filter_changes', **kwargs)


async def async_batch_eth_get_filter_changes(
    **kwargs,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_filter_changes', **kwargs
    )


def batch_eth_get_filter_logs(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_get_filter_logs', **kwargs)


async def async_batch_eth_get_filter_logs(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_filter_logs', **kwargs
    )


def batch_eth_get_logs(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_get_logs', **kwargs)


async def async_batch_eth_get_logs(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_get_logs', **kwargs)


def batch_eth_get_storage_at(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_get_storage_at', **kwargs)


async def async_batch_eth_get_storage_at(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_storage_at', **kwargs
    )


def batch_eth_get_transaction_by_block_hash_and_index(
    **kwargs,
) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute(
        'eth_get_transaction_by_block_hash_and_index', **kwargs
    )


async def async_batch_eth_get_transaction_by_block_hash_and_index(
    **kwargs,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_transaction_by_block_hash_and_index', **kwargs
    )


def batch_eth_get_transaction_by_block_number_and_index(
    **kwargs,
) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute(
        'eth_get_transaction_by_block_number_and_index', **kwargs
    )


async def async_batch_eth_get_transaction_by_block_number_and_index(
    **kwargs,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_transaction_by_block_number_and_index', **kwargs
    )


def batch_eth_get_transaction_by_hash(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute(
        'eth_get_transaction_by_hash', **kwargs
    )


async def async_batch_eth_get_transaction_by_hash(
    **kwargs,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_transaction_by_hash', **kwargs
    )


def batch_eth_get_transaction_count(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_get_transaction_count', **kwargs)


async def async_batch_eth_get_transaction_count(
    **kwargs,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_transaction_count', **kwargs
    )


def batch_eth_get_transaction_receipt(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute(
        'eth_get_transaction_receipt', **kwargs
    )


async def async_batch_eth_get_transaction_receipt(
    **kwargs,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_transaction_receipt', **kwargs
    )


def batch_eth_get_uncle_by_block_hash_and_index(
    **kwargs,
) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute(
        'eth_get_uncle_by_block_hash_and_index', **kwargs
    )


async def async_batch_eth_get_uncle_by_block_hash_and_index(
    **kwargs,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_uncle_by_block_hash_and_index', **kwargs
    )


def batch_eth_get_uncle_by_block_number_and_index(
    **kwargs,
) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute(
        'eth_get_uncle_by_block_number_and_index', **kwargs
    )


async def async_batch_eth_get_uncle_by_block_number_and_index(
    **kwargs,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_uncle_by_block_number_and_index', **kwargs
    )


def batch_eth_get_uncle_count_by_block_hash(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute(
        'eth_get_uncle_count_by_block_hash', **kwargs
    )


async def async_batch_eth_get_uncle_count_by_block_hash(
    **kwargs,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_uncle_count_by_block_hash', **kwargs
    )


def batch_eth_get_uncle_count_by_block_number(
    **kwargs,
) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute(
        'eth_get_uncle_count_by_block_number', **kwargs
    )


async def async_batch_eth_get_uncle_count_by_block_number(
    **kwargs,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_uncle_count_by_block_number', **kwargs
    )


def batch_eth_get_work(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_get_work', **kwargs)


async def async_batch_eth_get_work(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_get_work', **kwargs)


def batch_eth_hashrate(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_hashrate', **kwargs)


async def async_batch_eth_hashrate(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_hashrate', **kwargs)


def batch_eth_mining(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_mining', **kwargs)


async def async_batch_eth_mining(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_mining', **kwargs)


def batch_eth_new_block_filter(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_new_block_filter', **kwargs)


async def async_batch_eth_new_block_filter(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_new_block_filter', **kwargs
    )


def batch_eth_new_filter(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_new_filter', **kwargs)


async def async_batch_eth_new_filter(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_new_filter', **kwargs)


def batch_eth_new_pending_transaction_filter(
    **kwargs,
) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute(
        'eth_new_pending_transaction_filter', **kwargs
    )


async def async_batch_eth_new_pending_transaction_filter(
    **kwargs,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_new_pending_transaction_filter', **kwargs
    )


def batch_eth_protocol_version(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_protocol_version', **kwargs)


async def async_batch_eth_protocol_version(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_protocol_version', **kwargs
    )


def batch_eth_send_raw_transaction(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_send_raw_transaction', **kwargs)


async def async_batch_eth_send_raw_transaction(
    **kwargs,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_send_raw_transaction', **kwargs
    )


def batch_eth_send_transaction(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_send_transaction', **kwargs)


async def async_batch_eth_send_transaction(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_send_transaction', **kwargs
    )


def batch_eth_sign(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_sign', **kwargs)


async def async_batch_eth_sign(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_sign', **kwargs)


def batch_eth_sign_transaction(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_sign_transaction', **kwargs)


async def async_batch_eth_sign_transaction(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_sign_transaction', **kwargs
    )


def batch_eth_submit_hashrate(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_submit_hashrate', **kwargs)


async def async_batch_eth_submit_hashrate(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_submit_hashrate', **kwargs
    )


def batch_eth_submit_work(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_submit_work', **kwargs)


async def async_batch_eth_submit_work(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_submit_work', **kwargs
    )


def batch_eth_syncing(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_syncing', **kwargs)


async def async_batch_eth_syncing(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_syncing', **kwargs)


def batch_eth_uninstall_filter(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('eth_uninstall_filter', **kwargs)


async def async_batch_eth_uninstall_filter(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_uninstall_filter', **kwargs
    )


def batch_net_listening(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('net_listening', **kwargs)


async def async_batch_net_listening(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('net_listening', **kwargs)


def batch_net_peer_count(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('net_peer_count', **kwargs)


async def async_batch_net_peer_count(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('net_peer_count', **kwargs)


def batch_net_version(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('net_version', **kwargs)


async def async_batch_net_version(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('net_version', **kwargs)


def batch_shh_add_to_group(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('shh_add_to_group', **kwargs)


async def async_batch_shh_add_to_group(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'shh_add_to_group', **kwargs
    )


def batch_shh_get_filter_changes(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('shh_get_filter_changes', **kwargs)


async def async_batch_shh_get_filter_changes(
    **kwargs,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'shh_get_filter_changes', **kwargs
    )


def batch_shh_get_messages(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('shh_get_messages', **kwargs)


async def async_batch_shh_get_messages(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'shh_get_messages', **kwargs
    )


def batch_shh_has_identity(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('shh_has_identity', **kwargs)


async def async_batch_shh_has_identity(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'shh_has_identity', **kwargs
    )


def batch_shh_new_filter(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('shh_new_filter', **kwargs)


async def async_batch_shh_new_filter(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('shh_new_filter', **kwargs)


def batch_shh_new_group(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('shh_new_group', **kwargs)


async def async_batch_shh_new_group(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('shh_new_group', **kwargs)


def batch_shh_new_identity(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('shh_new_identity', **kwargs)


async def async_batch_shh_new_identity(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'shh_new_identity', **kwargs
    )


def batch_shh_post(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('shh_post', **kwargs)


async def async_batch_shh_post(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('shh_post', **kwargs)


def batch_shh_uninstall_filter(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('shh_uninstall_filter', **kwargs)


async def async_batch_shh_uninstall_filter(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'shh_uninstall_filter', **kwargs
    )


def batch_shh_version(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('shh_version', **kwargs)


async def async_batch_shh_version(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('shh_version', **kwargs)


def batch_web3_client_version(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('web3_client_version', **kwargs)


async def async_batch_web3_client_version(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'web3_client_version', **kwargs
    )


def batch_web3_sha3(**kwargs) -> spec.RpcPluralResponse:
    return rpc_batch_utils.batch_execute('web3_sha3', **kwargs)


async def async_batch_web3_sha3(**kwargs) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('web3_sha3', **kwargs)

