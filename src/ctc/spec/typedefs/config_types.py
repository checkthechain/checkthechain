from __future__ import annotations

import typing
from typing_extensions import TypedDict

from . import context_types
from . import network_types
from . import rpc_types

if typing.TYPE_CHECKING:
    import toolsql
    import toolcli
    import toolstr


class PartialConfig(TypedDict, total=False):
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

    global_cache_override: context_types.PartialSingleCacheContext
    network_cache_configs: typing.Mapping[
        network_types.ChainId,
        context_types.PartialMultiCacheContext,
    ]
    schema_cache_configs: context_types.PartialMultiCacheContext
    default_cache_config: context_types.SingleCacheContext

    log_rpc_calls: bool
    log_sql_queries: bool

    cli_color_theme: toolcli.StyleTheme
    cli_chart_charset: toolstr.SampleMode


class Config(TypedDict):
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

    global_cache_override: context_types.PartialSingleCacheContext
    network_cache_configs: typing.Mapping[
        network_types.ChainId,
        context_types.PartialMultiCacheContext,
    ]
    schema_cache_configs: context_types.PartialMultiCacheContext
    default_cache_config: context_types.SingleCacheContext

    log_rpc_calls: bool
    log_sql_queries: bool

    cli_color_theme: toolcli.StyleTheme
    cli_chart_charset: toolstr.SampleMode


class JsonConfig(TypedDict):
    config_spec_version: str
    data_dir: str
    providers: typing.Mapping[rpc_types.ProviderName, rpc_types.Provider]
    networks: typing.Mapping[str, network_types.NetworkMetadata]
    default_network: network_types.ChainId | None
    default_providers: typing.Mapping[str, rpc_types.ProviderName]

    db_configs: typing.Mapping[str, toolsql.DBConfig]

    global_cache_override: context_types.PartialSingleCacheContext
    network_cache_configs: typing.Mapping[
        str,
        context_types.PartialMultiCacheContext,
    ]
    schema_cache_configs: context_types.PartialMultiCacheContext
    default_cache_config: context_types.SingleCacheContext

    log_rpc_calls: bool
    log_sql_queries: bool

    cli_color_theme: toolcli.StyleTheme
    cli_chart_charset: toolstr.SampleMode

