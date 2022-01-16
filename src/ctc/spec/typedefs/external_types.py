import typing


if typing.TYPE_CHECKING:
    import numpy
    import pandas

    DataFrame = pandas.core.frame.DataFrame
    Series = pandas.core.series.Series
    DType = numpy.typing.DTypeLike
    NumpyArray = numpy.typing.NDArray

else:

    DataFrame = typing.Any
    Series = typing.Any
    DType = typing.Any
    NumpyArray = typing.Any

