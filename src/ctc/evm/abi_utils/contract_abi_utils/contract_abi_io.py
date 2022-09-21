from __future__ import annotations

from ctc import spec

from ... import address_utils
from . import contract_abi_modification


async def async_get_contract_abi(
    contract_address: spec.Address,
    *,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference = None,
    use_db: bool = True,
    db_query: bool | None = None,
    db_intake: bool | None = None,
    block: spec.BlockNumberReference | None = None,
    proxy_implementation: spec.Address | None = None,
    verbose: bool = True,
) -> spec.ContractABI:
    """retrieve abi of contract either from local database or block explorer

    for addresses that change ABI's over time, use db_query=False to skip cache
    """

    if db_query is None:
        db_query = use_db
    if db_intake is None:
        db_intake = use_db

    if network is None:
        from ctc import rpc
        network = rpc.get_provider_network(provider)

    # load from db
    if db_query:
        from ctc import db

        abi = await db.async_query_contract_abi(
            address=contract_address,
            network=network,
        )
        if abi is not None:
            return abi

    from ctc.protocols import etherscan_utils

    # load from block explorer
    abi = await etherscan_utils.async_get_contract_abi(
        contract_address,
        network=network,
        verbose=verbose,
    )

    # get proxy implementation
    if provider is None:
        provider = {'network': network}
    if proxy_implementation is None:
        proxy_implementation = (
            await address_utils.async_get_proxy_implementation(
                contract_address=contract_address,
                provider=provider,
                block=block,
            )
        )

    # get proxy abi
    includes_proxy = False
    if proxy_implementation is not None:
        proxy_abi = await etherscan_utils.async_get_contract_abi(
            contract_address=proxy_implementation,
            network=network,
            verbose=verbose,
        )
        abi = contract_abi_modification.combine_contract_abis([abi, proxy_abi])
        includes_proxy = True

    # save to db
    if db_intake:
        from ctc import db

        await db.async_intake_contract_abi(
            contract_address=contract_address,
            network=network,
            abi=abi,
            includes_proxy=includes_proxy,
        )

    return abi
