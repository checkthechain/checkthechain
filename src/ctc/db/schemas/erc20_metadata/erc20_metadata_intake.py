from __future__ import annotations

import os
import typing

import toolcache

from ctc import config
from ctc import directory
from ctc import spec
from ctc.toolbox import store_utils
from .. import connect_utils
from . import erc20_metadata_statements


async def async_intake_default_tokens(
    network: spec.NetworkReference = 'mainnet',
) -> None:
    if network not in ['mainnet', 1]:
        print('no default tokens for network: ' + str(network))
        return

    # create engine
    engine = connect_utils.create_engine(
        schema_name='erc20_metadata',
        network=network,
    )
    if engine is None:
        return

    data = load_filesystem_erc20_data('mainnet')
    with engine.begin() as conn:
        await erc20_metadata_statements.async_upsert_erc20s_metadata(
            erc20s_metadata=data,
            conn=conn,
            network=network,
        )


@toolcache.cache('memory')
def load_filesystem_erc20_data(
    network: spec.NetworkReference,
    label: typing.Optional[str] = None,
) -> list[spec.ERC20Metadata]:

    # set default label
    if label is None:
        label = '1inch'

    # build path
    path = _get_erc20_data_path(network=network, label=label)

    # load data
    return store_utils.load_file_data(path)


def _get_erc20_data_path(network: spec.NetworkReference, label: str) -> str:
    network_name = directory.get_network_name(network=network)
    data_dir = config.get_data_dir()
    filename = label + '.csv'
    return os.path.join(data_dir, network_name, 'erc20s', filename)
