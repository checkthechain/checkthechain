import typing

if typing.TYPE_CHECKING:
    import numpy
    import pandas


DataFrame = typing.Type['pandas.core.frame.DataFrame']
DType = typing.Type['numpy.typing.DTypeLike']
