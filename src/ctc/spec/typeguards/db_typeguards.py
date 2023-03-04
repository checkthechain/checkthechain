from __future__ import annotations

import typing

from . import typedata

if typing.TYPE_CHECKING:
    from typing_extensions import TypeGuard
    from . import typedefs


def is_schema_name(value: typing.Any) -> TypeGuard[typedefs.SchemaName]:
    return value in typedata.schema_names

