from __future__ import annotations

import typing

from ctc import spec

if typing.TYPE_CHECKING:
    from typing_extensions import TypeGuard

    from .. import typedefs


def is_polars_dataframe(item: typing.Any) -> TypeGuard[spec.DataFrame]:
    """return whether input is a polars DataFrame"""
    item_type = type(item)
    return (
        item_type.__name__ == 'DataFrame'
        and item_type.__module__ == 'polars.internals.dataframe.frame'
    )


def is_polars_series(item: typing.Any) -> TypeGuard[spec.DataFrame]:
    """return whether input is a polars DataFrame"""
    item_type = type(item)
    return item_type.__name__ == 'Series' and item_type.__module__.startswith(
        'polars'
    )


def is_int(value: typing.Any) -> TypeGuard['typedefs.Integer']:
    """return whether input is a python int or numpy int"""
    return isinstance(value, int) or type(value).__name__ in (
        'int8',
        'int16',
        'int32',
        'int64',
    )


def is_float(value: typing.Any) -> TypeGuard['typedefs.Float']:
    """return whether input is a python float or numpy float"""
    return isinstance(value, float) or type(value).__name__ in (
        'float16',
        'float32',
        'float64',
        'float128',
    )


def is_number(value: typing.Any) -> TypeGuard['typedefs.Number']:
    """return whether input is any type of int or float"""
    return is_int(value) or is_float(value)

