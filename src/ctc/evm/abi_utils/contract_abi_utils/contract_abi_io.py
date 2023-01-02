from __future__ import annotations

from ctc import spec

from ... import contract_utils
from . import contract_abi_modification


async def async_get_contract_abi(
    contract_address: spec.Address,
    *,
    block: spec.BlockNumberReference | None = None,
    proxy_implementation: spec.Address | None = None,
    verbose: bool = True,
    context: spec.Context = None,
) -> spec.ContractABI:
    """retrieve abi of contract either from local database or block explorer

    for addresses that change ABI's over time, use db_query=False to skip cache
    """
    from ctc import config

    # load from db
    read_cache, write_cache = config.get_context_cache_read_write(
        context=context, schema_name='contract_abis'
    )
    if read_cache:
        from ctc import db

        abi = await db.async_query_contract_abi(
            address=contract_address,
            context=context,
        )
        if abi is not None:
            return abi

    from ctc.protocols import etherscan_utils

    # load from block explorer
    abi = await etherscan_utils.async_get_contract_abi(
        contract_address,
        context=context,
        verbose=verbose,
    )

    # get proxy implementation
    if proxy_implementation is None:
        proxy_implementation = (
            await contract_utils.async_get_proxy_implementation(
                contract_address=contract_address,
                context=context,
                block=block,
            )
        )

    # get proxy abi
    includes_proxy = False
    if proxy_implementation is not None:
        proxy_abi = await etherscan_utils.async_get_contract_abi(
            contract_address=proxy_implementation,
            context=context,
            verbose=verbose,
        )
        abi = contract_abi_modification.combine_contract_abis([abi, proxy_abi])
        includes_proxy = True

    # save to db
    if write_cache:
        from ctc import db

        await db.async_intake_contract_abi(
            contract_address=contract_address,
            context=context,
            abi=abi,
            includes_proxy=includes_proxy,
        )

    return abi

