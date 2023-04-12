from __future__ import annotations

from ctc import evm
from ctc import spec
from . import abi_crud
from . import url_crud


async def async_open_etherscan_in_browser(
    query: str,
    *,
    logs: bool | None = None,
    changes: bool | None = None,
    holdings: bool | None = None,
    erc20_transfers: bool | None = None,
    internal: bool | None = None,
    holders: bool | None = None,
    abi: bool | None = None,
    context: spec.Context | None = None,
) -> None:

    import toolcli
    import ctc.config

    if ctc.config.get_context_chain_id(context) != 1:
        raise NotImplementedError('only currently implemented for ethereum')

    is_address = False
    if query.startswith('0x') and len(query) == 42:
        url = url_crud.create_address_url(query)
        address = query
        is_address = True
    elif query.startswith('0x') and len(query) == 66:
        if logs:
            url = url_crud.create_transaction_logs_url(query)
        elif changes:
            url = url_crud.create_transaction_state_changes_url(query)
        else:
            url = url_crud.create_transaction_url(query)
    elif query.isnumeric():
        url = url_crud.create_block_url(int(query))
    elif query.endswith('.eth'):
        from ctc.protocols import ens_utils

        resolved_address = await ens_utils.async_resolve_name(query)
        if resolved_address is None:
            print('[name does not resolve to an address]')
        else:
            address = resolved_address
            url = url_crud.create_address_url(address)
            is_address = True
    else:
        try:
            address = await evm.async_get_erc20_address(query)
            url = url_crud.create_address_url(address)
            is_address = True
        except Exception:
            raise Exception('unknown query: ' + str(query))

    if is_address:
        if holdings:
            url = url_crud.create_address_holdings_url(address)
        elif erc20_transfers:
            url = url_crud.create_address_erc20_transfers_url(address)
        elif internal:
            url = url_crud.create_address_internal_txs_url(address)
        elif holders:
            url = url_crud.create_token_holders_url(address)

    if abi:
        if is_address:
            import json

            raw_abi = await abi_crud.async_get_contract_abi(
                address, verbose=False
            )
            print(json.dumps(raw_abi, sort_keys=True, indent=4))
        else:
            raise Exception('can only use abi option for addresses')
    else:
        toolcli.open_url_in_browser(url)

