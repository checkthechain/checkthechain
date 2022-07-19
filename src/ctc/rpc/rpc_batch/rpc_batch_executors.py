from __future__ import annotations

import typing

from ctc import evm
from ctc import spec

from .. import rpc_provider
from . import rpc_batch_utils


async def async_batch_eth_accounts(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_accounts', **kwargs)


async def async_batch_eth_block_number(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_block_number', **kwargs
    )


async def async_batch_eth_call(
    *,
    function_abi: spec.FunctionABI | None = None,
    function_name: str | None = None,
    function_selector: spec.FunctionSelector | None = None,
    provider: spec.ProviderReference = None,
    to_address: spec.Address | None = None,
    to_addresses: typing.Sequence[spec.Address] | None = None,
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:

    if function_abi is None:

        if to_address is not None:
            contract_address = to_address
        elif to_addresses is not None:
            contract_address = to_addresses[0]
        else:
            raise Exception(
                'must specify to_address or to_addresses'
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


async def async_batch_eth_coinbase(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_coinbase', **kwargs)


async def async_batch_eth_compile_lll(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_compile_lll', **kwargs
    )


async def async_batch_eth_compile_serpent(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_compile_serpent', **kwargs
    )


async def async_batch_eth_compile_solidity(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_compile_solidity', **kwargs
    )


async def async_batch_eth_estimate_gas(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_estimate_gas', **kwargs
    )


async def async_batch_eth_gas_price(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_gas_price', **kwargs)


async def async_batch_eth_get_balance(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_balance', **kwargs
    )


async def async_batch_eth_get_block_by_hash(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_block_by_hash', **kwargs
    )


async def async_batch_eth_get_block_by_number(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_block_by_number', **kwargs
    )


async def async_batch_eth_get_block_transaction_count_by_hash(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_block_transaction_count_by_hash', **kwargs
    )


async def async_batch_eth_get_block_transaction_count_by_number(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_block_transaction_count_by_number', **kwargs
    )


async def async_batch_eth_get_code(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_get_code', **kwargs)


async def async_batch_eth_get_compilers(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_compilers', **kwargs
    )


async def async_batch_eth_get_filter_changes(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_filter_changes', **kwargs
    )


async def async_batch_eth_get_filter_logs(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_filter_logs', **kwargs
    )


async def async_batch_eth_get_logs(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_get_logs', **kwargs)


async def async_batch_eth_get_storage_at(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_storage_at', **kwargs
    )


async def async_batch_eth_get_transaction_by_block_hash_and_index(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_transaction_by_block_hash_and_index', **kwargs
    )


async def async_batch_eth_get_transaction_by_block_number_and_index(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_transaction_by_block_number_and_index', **kwargs
    )


async def async_batch_eth_get_transaction_by_hash(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_transaction_by_hash', **kwargs
    )


async def async_batch_eth_get_transaction_count(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_transaction_count', **kwargs
    )


async def async_batch_eth_get_transaction_receipt(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_transaction_receipt', **kwargs
    )


async def async_batch_eth_get_uncle_by_block_hash_and_index(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_uncle_by_block_hash_and_index', **kwargs
    )


async def async_batch_eth_get_uncle_by_block_number_and_index(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_uncle_by_block_number_and_index', **kwargs
    )


async def async_batch_eth_get_uncle_count_by_block_hash(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_uncle_count_by_block_hash', **kwargs
    )


async def async_batch_eth_get_uncle_count_by_block_number(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_get_uncle_count_by_block_number', **kwargs
    )


async def async_batch_eth_get_work(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_get_work', **kwargs)


async def async_batch_eth_hashrate(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_hashrate', **kwargs)


async def async_batch_eth_mining(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_mining', **kwargs)


async def async_batch_eth_new_block_filter(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_new_block_filter', **kwargs
    )


async def async_batch_eth_new_filter(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_new_filter', **kwargs)


async def async_batch_eth_new_pending_transaction_filter(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_new_pending_transaction_filter', **kwargs
    )


async def async_batch_eth_protocol_version(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_protocol_version', **kwargs
    )


async def async_batch_eth_send_raw_transaction(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_send_raw_transaction', **kwargs
    )


async def async_batch_eth_send_transaction(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_send_transaction', **kwargs
    )


async def async_batch_eth_sign(**kwargs: typing.Any) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_sign', **kwargs)


async def async_batch_eth_sign_transaction(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_sign_transaction', **kwargs
    )


async def async_batch_eth_submit_hashrate(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_submit_hashrate', **kwargs
    )


async def async_batch_eth_submit_work(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_submit_work', **kwargs
    )


async def async_batch_eth_syncing(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_syncing', **kwargs)


async def async_batch_eth_chain_id(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('eth_chain_id', **kwargs)


async def async_batch_eth_uninstall_filter(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'eth_uninstall_filter', **kwargs
    )


async def async_batch_net_listening(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('net_listening', **kwargs)


async def async_batch_net_peer_count(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('net_peer_count', **kwargs)


async def async_batch_net_version(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('net_version', **kwargs)


async def async_batch_shh_add_to_group(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'shh_add_to_group', **kwargs
    )


async def async_batch_shh_get_filter_changes(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'shh_get_filter_changes', **kwargs
    )


async def async_batch_shh_get_messages(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'shh_get_messages', **kwargs
    )


async def async_batch_shh_has_identity(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'shh_has_identity', **kwargs
    )


async def async_batch_shh_new_filter(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('shh_new_filter', **kwargs)


async def async_batch_shh_new_group(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('shh_new_group', **kwargs)


async def async_batch_shh_new_identity(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'shh_new_identity', **kwargs
    )


async def async_batch_shh_post(**kwargs: typing.Any) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('shh_post', **kwargs)


async def async_batch_shh_uninstall_filter(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'shh_uninstall_filter', **kwargs
    )


async def async_batch_shh_version(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('shh_version', **kwargs)


async def async_batch_web3_client_version(
    **kwargs: typing.Any,
) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute(
        'web3_client_version', **kwargs
    )


async def async_batch_web3_sha3(**kwargs: typing.Any) -> spec.RpcPluralResponse:
    return await rpc_batch_utils.async_batch_execute('web3_sha3', **kwargs)
