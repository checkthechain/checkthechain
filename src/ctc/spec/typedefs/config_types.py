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
    providers: typing.Mapping[str, rpc_types.Provider]
    networks: typing.Mapping[
        network_types.ChainId, network_types.NetworkMetadata
    ]
    default_network: network_types.ChainId
    default_providers: typing.Mapping[network_types.ChainId, str]
    db_configs: typing.Mapping[str, toolsql.DBConfig]
    context_cache_rules: typing.Sequence[context_types.ContextCacheRule]

    log_rpc_calls: bool
    log_sql_queries: bool

    cli_color_theme: toolcli.StyleTheme
    cli_chart_charset: toolstr.SampleMode


class Config(TypedDict):
    config_spec_version: str
    data_dir: str
    providers: typing.Mapping[str, rpc_types.Provider]
    networks: typing.Mapping[
        network_types.ChainId, network_types.NetworkMetadata
    ]
    default_network: network_types.ChainId
    default_providers: typing.Mapping[network_types.ChainId, str]

    db_configs: typing.Mapping[str, toolsql.DBConfig]
    context_cache_rules: typing.Sequence[context_types.ContextCacheRule]

    log_rpc_calls: bool
    log_sql_queries: bool

    cli_color_theme: toolcli.StyleTheme
    cli_chart_charset: toolstr.SampleMode


class JsonConfig(TypedDict):
    config_spec_version: str
    data_dir: str
    providers: typing.Mapping[str, rpc_types.Provider]
    networks: typing.Mapping[str, network_types.NetworkMetadata]
    default_network: network_types.ChainId
    default_providers: typing.Mapping[str, str]

    db_configs: typing.Mapping[str, toolsql.DBConfig]
    context_cache_rules: typing.Sequence[context_types.ContextCacheRule]

    log_rpc_calls: bool
    log_sql_queries: bool

    cli_color_theme: toolcli.StyleTheme
    cli_chart_charset: toolstr.SampleMode

