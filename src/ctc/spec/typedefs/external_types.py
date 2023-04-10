from __future__ import annotations

import typing


if typing.TYPE_CHECKING:
    import numpy
    import polars as pl
    import pandas as pd  # type: ignore

    PolarsDataFrame = pl.DataFrame
    PandasDataFrame = pd.DataFrame
    DataFrame = pd.core.frame.DataFrame
    Series = pd.core.series.Series[typing.Any]
    PandasIndex = pd.core.indexes.base.Index
    DType = numpy.typing.DTypeLike
    NumpyArray = numpy.typing.NDArray  # type: ignore

    IntegerOutputFormatScalar = typing.Union[
        type[pl.datatypes.DataTypeClass],
        type[object],
        type[int],
    ]
    IntegerOutputFormat = typing.Union[
        IntegerOutputFormatScalar,
        typing.Mapping[str, IntegerOutputFormatScalar],
    ]

else:
    DataFrame = typing.Any
    Series = typing.Any
    PandasIndex = typing.Any
    DType = typing.Any
    NumpyArray = typing.Any


Integer = typing.Union[
    int,
    'numpy.int8',
    'numpy.int16',
    'numpy.int32',
    'numpy.int64',
]

Float = typing.Union[
    float,
    'numpy.float16',
    'numpy.float32',
    'numpy.float64',
    'numpy.float128',
]

Number = typing.Union[Integer, Float]

