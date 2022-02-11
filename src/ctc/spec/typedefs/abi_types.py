# see https://docs.soliditylang.org/en/latest/abi-spec.html

from __future__ import annotations

import typing
from typing_extensions import TypedDict

if typing.TYPE_CHECKING:
    from typing_extensions import NotRequired


class FunctionABI(TypedDict):
    type: typing.Literal['function', 'constructor', 'receive', 'fallback']
    name: NotRequired[str]
    inputs: NotRequired[list['ABIFunctionArg']]
    outputs: NotRequired[list['ABIFunctionArg']]
    stateMutability: typing.Literal['pure', 'view', 'nonpayable', 'payable']


class ABIFunctionArg(TypedDict):
    name: str
    type: 'ABIDatumType'
    components: 'ABITupleComponents'


class EventABI(TypedDict):
    type: typing.Literal['event']
    name: str
    inputs: list['ABIEventArg']


class ABIEventArg(TypedDict):
    name: str
    type: 'ABIDatumType'
    components: 'ABITupleComponents'
    indexed: bool
    anonymous: NotRequired[bool]


class ErrorABI(TypedDict):
    type: typing.Literal['error']
    name: str
    inputs: ABIFunctionArg


ContractABI = typing.List[typing.Union[FunctionABI, EventABI, ErrorABI]]


ABITupleComponents = typing.List['ABITupleComponent']

ABITupleComponent = dict

# # class ABITupleComponent(TypedDict):
# #     name: str
# #     type: ABIDatumType
# #     components: NotRequired['ABITupleComponents']


ABIDatumType = str
ABIDatatypeStr = str
FunctionSelector = str
FunctionSignature = str


class DecodedCallData(TypedDict):
    function_abi: FunctionABI
    function_selector: str
    parameters: list[typing.Any]
    named_parameters: typing.Optional[dict[str, typing.Any]]

