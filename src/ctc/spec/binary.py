import typing


BinaryData = typing.Union[bytes, str]
BlockSpec = typing.Union[
    int, BinaryData, typing.Literal['latest', 'earliest', 'pending']
]

