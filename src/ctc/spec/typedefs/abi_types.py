# see https://docs.soliditylang.org/en/latest/abi-spec.html

from __future__ import annotations

import typing
from typing_extensions import TypedDict

if typing.TYPE_CHECKING:
    from typing_extensions import NotRequired


class FunctionABI(TypedDict, total=False):
    type: typing.Literal['function', 'constructor', 'receive', 'fallback']
    name: NotRequired[str]
    inputs: NotRequired[list['ABIFunctionArg']]
    outputs: NotRequired[list['ABIFunctionArg']]
    stateMutability: NotRequired[typing.Literal['pure', 'view', 'nonpayable', 'payable']]
    anonymous: NotRequired[bool]


class ABIFunctionArg(TypedDict, total=False):
    name: str
    type: 'ABIDatumType'
    components: 'ABITupleComponents'
    internalType: 'ABIDatumType'


class EventABI(TypedDict, total=False):
    type: typing.Literal['event']
    name: str
    inputs: list['ABIEventArg']
    anonymous: bool


class ABIEventArg(TypedDict, total=False):
    name: str
    type: 'ABIDatumType'
    internalType: 'ABIDatumType'
    components: 'ABITupleComponents'
    indexed: bool
    anonymous: NotRequired[bool]


class ErrorABI(TypedDict):
    type: typing.Literal['error']
    name: str
    inputs: ABIFunctionArg


ContractABIEntry = typing.Union[FunctionABI, EventABI, ErrorABI]
ContractABI = typing.List[ContractABIEntry]


ABITupleComponents = typing.List['ABITupleComponent']

ABITupleComponent = typing.Mapping[typing.Any, typing.Any]

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
    parameters: typing.List[typing.Any]
    named_parameters: typing.Optional[typing.Mapping[str, typing.Any]]
