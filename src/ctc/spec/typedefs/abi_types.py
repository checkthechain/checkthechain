# see https://docs.soliditylang.org/en/latest/abi-spec.html

import typing
from typing_extensions import NotRequired


class FunctionABI(typing.TypedDict):
    type: typing.Literal['function', 'constructor', 'receive', 'fallback']
    name: NotRequired[str]
    inputs: NotRequired[list['ABIFunctionArg']]
    outputs: NotRequired[list['ABIFunctionArg']]
    stateMutability: typing.Literal['pure', 'view', 'nonpayable', 'payable']


class ABIFunctionArg(typing.TypedDict):
    name: str
    type: 'ABIDatumType'
    components: 'ABITupleComponents'


class EventABI(typing.TypedDict):
    type: typing.Literal['event']
    name: str
    inputs: list['ABIEventArg']


class ABIEventArg(typing.TypedDict):
    name: str
    type: 'ABIDatumType'
    components: 'ABITupleComponents'
    indexed: bool
    anonymous: NotRequired[bool]


class ErrorABI(typing.TypedDict):
    type: typing.Literal['error']
    name: str
    inputs: ABIFunctionArg


ContractABI = list[typing.Union[FunctionABI, EventABI, ErrorABI]]


ABITupleComponents = list['ABITupleComponent']

ABITupleComponent = dict

# # class ABITupleComponent(typing.TypedDict):
# #     name: str
# #     type: ABIDatumType
# #     components: NotRequired['ABITupleComponents']


ABIDatumType = str
ABIDatatypeStr = str
FunctionSelector = str
FunctionSignature = str


class DecodedCallData(typing.TypedDict):
    function_abi: FunctionABI
    function_selector: str
    parameters: list[typing.Any]
    named_parameters: typing.Optional[dict[str, typing.Any]]

