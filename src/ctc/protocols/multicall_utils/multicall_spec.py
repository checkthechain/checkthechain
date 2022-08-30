from __future__ import annotations

import typing
from typing_extensions import TypedDict

if typing.TYPE_CHECKING:
    from typing_extensions import NotRequired

from ctc import spec


#
# # calls
#

if typing.TYPE_CHECKING:
    FunctionParameterList = typing.Sequence[typing.Any]
    FunctionParameterMap = typing.Mapping[str, typing.Any]
    FunctionParameters = typing.Union[
        FunctionParameterList, FunctionParameterMap
    ]

    UnencodedCallTuple = typing.Union[
        typing.Tuple[
            spec.Address,
            typing.Union[spec.FunctionABI, str],
        ],
        typing.Tuple[
            spec.Address,
            typing.Union[spec.FunctionABI, str],
            typing.Union[FunctionParameterList, FunctionParameterMap],
        ],
    ]
    UnencodedCallList = typing.Sequence[typing.Any]

    class UnencodedCallDict(TypedDict):
        contract: spec.Address
        function: typing.Union[spec.FunctionABI, str]
        function_parameters: NotRequired[FunctionParameters]

    UnencodedCall = typing.Union[
        UnencodedCallTuple,
        UnencodedCallList,
        UnencodedCallDict,
    ]

    EncodedCallTuple = typing.Tuple[spec.Address, spec.BinaryData]
    EncodedCallList = typing.Sequence[typing.Any]

    class EncodedCallDict(TypedDict):
        contract: spec.Address
        call_data: spec.BinaryData

    EncodedCall = typing.Union[
        EncodedCallTuple, EncodedCallList, EncodedCallDict
    ]

    Call = typing.Union[UnencodedCall, EncodedCall]
