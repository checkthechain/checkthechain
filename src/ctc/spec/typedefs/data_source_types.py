from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import toolsql

from typing_extensions import Literal
from typing_extensions import TypedDict

from . import rpc_types


BackendType = Literal['filesystem', 'rpc', 'db', 'rest', 'hybrid']


class DataSource(TypedDict, total=False):
    """rpc_typesifies a location to use for retrieving data

    - if source parameters are missing, system defaults are used
    - for hybrid sources, will try sources in order until one succeeds
        - will insert result into earlier source if hybrid_backfill=True
    """

    # backend type
    backend: BackendType

    # source parameters
    db_config: toolsql.DBConfig
    rest_endpoint: dict[str, typing.Any]
    filesystem_root: str
    provider: rpc_types.ProviderReference | None

    # hybrid parameters
    hybrid_order: typing.Sequence['LeafDataSource']
    hybrid_backfill: bool


class LeafDataSource(TypedDict, total=False):

    # backend type
    backend: BackendType

    # source parameters
    db_config: toolsql.DBConfig
    rest_endpoint: str
    filesystem_root: str
    provider: rpc_types.ProviderReference
