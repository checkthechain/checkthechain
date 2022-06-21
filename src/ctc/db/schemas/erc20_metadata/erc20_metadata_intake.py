from __future__ import annotations

import os

from ctc import config
from ctc import evm
from ctc import spec
from .. import connect_utils
from . import erc20_metadata_statements


async def async_intake_default_tokens(
    network: spec.NetworkReference = 'mainnet',
    verbose: bool = True,
) -> None:

    from ctc.evm.erc20_utils import erc20_defaults

    if network not in ['mainnet', 1]:
        print('no default tokens for network: ' + str(network))
        return

    # load data
    data = erc20_defaults.load_default_erc20s(network=network)

    # create engine
    engine = connect_utils.create_engine(
        schema_name='erc20_metadata',
        network=network,
    )
    if engine is None:
        return

    # write to db
    with engine.begin() as conn:
        await erc20_metadata_statements.async_upsert_erc20s_metadata(
            erc20s_metadata=data,
            conn=conn,
            network=network,
        )

    # print summary
    if verbose:
        print('added metadata of', len(data), 'default ERC20 tokens to db')


def _get_erc20_data_path(network: spec.NetworkReference, label: str) -> str:
    if network is None:
        network = config.get_default_network()
    network_name = evm.get_network_name(network=network, require=True)
    data_dir = config.get_data_dir()
    filename = label + '.csv'
    return os.path.join(data_dir, network_name, 'erc20s', filename)


async def async_intake_erc20_metadata(
    address: spec.Address,
    network: spec.NetworkReference,
    decimals: int | None = None,
    symbol: str | None = None,
    name: str | None = None,
) -> None:

    engine = connect_utils.create_engine(
        schema_name='erc20_metadata',
        network=network,
    )
    if engine is None:
        return
    with engine.begin() as conn:
        await erc20_metadata_statements.async_upsert_erc20_metadata(
            conn=conn,
            network=network,
            address=address,
            decimals=decimals,
            symbol=symbol,
            name=name,
        )
