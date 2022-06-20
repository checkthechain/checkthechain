from __future__ import annotations

import typing
from typing_extensions import TypedDict

from . import network_types
from . import rpc_types

if typing.TYPE_CHECKING:
    import toolsql


class PartialConfigSpec(TypedDict, total=False):
    config_spec_version: str
    data_dir: str
    providers: typing.Mapping[rpc_types.ProviderName, rpc_types.Provider]
    networks: typing.Mapping[
        network_types.ChainId, network_types.NetworkMetadata
    ]
    default_network: network_types.ChainId | None
    default_providers: typing.Mapping[
        network_types.ChainId, rpc_types.ProviderName
    ]
    db_configs: typing.Mapping[str, toolsql.DBConfig]

    log_rpc_calls: bool
    log_sql_queries: bool


class ConfigSpec(TypedDict):
    config_spec_version: str
    data_dir: str
    providers: typing.Mapping[rpc_types.ProviderName, rpc_types.Provider]
    networks: typing.Mapping[
        network_types.ChainId, network_types.NetworkMetadata
    ]
    default_network: network_types.ChainId | None
    default_providers: typing.Mapping[
        network_types.ChainId, rpc_types.ProviderName
    ]

    db_configs: typing.Mapping[str, toolsql.DBConfig]

    log_rpc_calls: bool
    log_sql_queries: bool
