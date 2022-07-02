"""Track legacy type specification of Config starting from version 0.2.1

These definitions should be mostly self-contained
- do not want them altered by upstream changes to definition
- thus, provide definitions for:
    - Provider
    - NetworkMetadata
    - toolsql.DBConfig
"""

from __future__ import annotations

import typing

from typing_extensions import Literal
from typing_extensions import TypedDict

from ctc import spec


class LegacyConfig__3_0_0(TypedDict):
    config_spec_version: str
    data_dir: str
    providers: typing.Mapping[spec.ProviderName, LegacyProvider__0_3_0]
    networks: typing.Mapping[spec.ChainId, LegacyNetworkMetadata__0_3_0]
    default_network: spec.ChainId | None
    default_providers: typing.Mapping[spec.ChainId, spec.ProviderName]
    db_configs: typing.Mapping[str, ToolsqlDBConfig]
    log_rpc_calls: bool
    log_sql_queries: bool


class LegacyConfig__0_2_3(TypedDict):
    config_spec_version: str
    data_dir: str
    providers: typing.Mapping[spec.ProviderName, LegacyProvider__0_2_1]
    networks: typing.Mapping[spec.NetworkName, LegacyNetworkMetadata__0_2_1]
    network_defaults: LegacyConfigNetworkDefaults


class LegacyConfig__0_2_1(TypedDict):
    version: str
    data_dir: str
    providers: typing.Mapping[spec.ProviderName, LegacyProvider__0_2_1]
    networks: typing.Mapping[spec.NetworkName, LegacyNetworkMetadata__0_2_1]
    network_defaults: LegacyConfigNetworkDefaults


class LegacyConfigNetworkDefaults(TypedDict):
    default_network: spec.NetworkName
    default_providers: typing.Mapping[spec.NetworkName, spec.ProviderName]


#
# # network metadata
#


class LegacyNetworkMetadata__0_3_0(TypedDict):
    name: str | None
    chain_id: int
    block_explorer: str | None


class LegacyNetworkMetadata__0_2_1(TypedDict):
    name: str
    chain_id: int
    block_explorer: str


#
# # provider
#


class LegacyProvider__0_3_0(TypedDict, total=True):
    url: str
    name: typing.Optional[str]
    network: typing.Optional[str | int]
    protocol: Literal['http', 'wss', 'ipc']
    session_kwargs: typing.Optional[typing.Mapping[typing.Any, typing.Any]]
    chunk_size: typing.Optional[int]


class LegacyProvider__0_2_1(TypedDict, total=True):
    url: str
    name: typing.Optional[str]
    network: typing.Optional[str]
    protocol: Literal['http', 'wss', 'ipc']
    session_kwargs: typing.Optional[typing.Mapping[typing.Any, typing.Any]]
    chunk_size: typing.Optional[int]


#
# # toolsql
#


class ToolsqlDBConfig(TypedDict, total=False):
    dbms: Literal['sqlite', 'postgresql']
    path: str
    engine: str
    hostname: str
    port: int
    database: str
    username: str
    password: str
    socket: str
    socket_dir: str
    timeout: typing.Union[int, float]
    pool_timeout: typing.Union[int, float]
