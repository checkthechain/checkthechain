from __future__ import annotations

import typing

from typing_extensions import Literal, TypedDict, TypeAlias

from . import binary_types
from . import transaction_types


TraceOutputType = Literal['trace', 'stateDiff', 'vmTrace']
TraceItemType = Literal['call', 'create', 'suicide', 'reward']
TraceCallType = Literal['call', 'staticcall', 'delegatecall']


TraceCallAction = TypedDict(
    'TraceCallAction',
    {
        'from': str,
        'gas': int,
        'value': int,
        #
        # call-specific keys
        'call_type': TraceCallType,
        'input': str,
        'to': str,
    },
)

TraceCreateAction = TypedDict(
    'TraceCreateAction',
    {
        'from': str,
        'gas': int,
        'value': int,
        #
        # create-specific keys
        'init': str,
    },
)


TraceSuicideAction = TypedDict(
    'TraceSuicideAction',
    {
        'from': str,
        'gas': int,
        'value': int,
        #
        # suicide-specific keys
        'init': str,
    },
)


class TraceRewardAction(TypedDict):
    value: int
    author: str
    reward_type: Literal['block', 'uncle']


TraceAction = typing.Union[
    TraceCreateAction,
    TraceCallAction,
    TraceSuicideAction,
    TraceRewardAction,
]


class TraceCallResult(TypedDict):
    gas_used: int
    output: str


class TraceCreateResult(TypedDict):
    gas_used: int
    address: str
    code: str


TraceSuicideResult: TypeAlias = None
TraceRewardResult: TypeAlias = None


TraceResult = typing.Union[
    TraceCallResult,
    TraceCreateResult,
    TraceSuicideResult,
    TraceRewardResult,
]


class SingleTrace(TypedDict):
    action: TraceAction
    block_hash: str
    block_number: int
    result: TraceResult
    subtraces: int
    trace_address: typing.Sequence[int]
    transaction_hash: str
    transaction_position: int
    type: TraceItemType


TraceList = typing.Sequence[SingleTrace]


IntegerStateDiffEqual = Literal['=']
IntegerFromTo = TypedDict('IntegerFromTo', {'from': int, 'to': int})
IntegerStateDiffMult = TypedDict('IntegerStateDiffMult', {'*': IntegerFromTo})
IntegerStateDiffAdd = TypedDict(
    'IntegerStateDiffAdd',
    {'+': int},
)
IntegerStateDiffSubtract = TypedDict(
    'IntegerStateDiffSubtract',
    {'-': int},
)
IntegerStateDiff = typing.Union[
    IntegerStateDiffMult,
    IntegerStateDiffAdd,
    IntegerStateDiffSubtract,
]


BinaryStateDiffEqual = Literal['=']
BinaryFromTo = TypedDict(
    'BinaryFromTo',
    {'from': binary_types.PrefixHexData, 'to': binary_types.PrefixHexData},
)
BinaryStateDiffMult = TypedDict('BinaryStateDiffMult', {'*': BinaryFromTo})
BinaryStateDiffAdd = TypedDict(
    'BinaryStateDiffAdd',
    {'+': binary_types.PrefixHexData},
)
BinaryStateDiffSubtract = TypedDict(
    'BinaryStateDiffSubtract',
    {'-': binary_types.PrefixHexData},
)
BinaryStateDiff = typing.Union[
    BinaryStateDiffMult,
    BinaryStateDiffAdd,
    BinaryStateDiffSubtract,
]


StorageStateDiffTrace = typing.Mapping[
    binary_types.PrefixHexData,
    BinaryStateDiff,
]


class AddressStateDiffTrace(TypedDict):
    balance: IntegerStateDiff
    code: BinaryStateDiff
    nonce: IntegerStateDiff
    storage: StorageStateDiffTrace


StateDiffTrace = typing.Mapping[
    transaction_types.TransactionHash, AddressStateDiffTrace
]


Opcode = str


class OpcodeExecutionMem(TypedDict):
    data: binary_types.PrefixHexData
    off: int


class OpcodeExecutionStore(TypedDict):
    key: binary_types.PrefixHexData
    val: binary_types.PrefixHexData


class OpcodeExecution(TypedDict):
    mem: None | OpcodeExecutionMem
    push: typing.Sequence[binary_types.PrefixHexData]
    store: None | OpcodeExecutionStore
    used: int


class OpcodeTrace(TypedDict):
    cost: int
    ex: None | OpcodeExecution
    pc: int
    sub: None | typing.Sequence['VMTrace']
    op: Opcode
    idx: str


class VMTrace(TypedDict):
    code: binary_types.PrefixHexData
    ops: typing.Sequence[OpcodeTrace]


class TraceReplayResult(TypedDict):
    trace: TraceList | None
    state_diff: StateDiffTrace | None
    vm_trace: VMTrace | None


#
# # debug traces
#


class DebugTransactionTrace(TypedDict):
    gas: int
    failed: bool
    return_value: str
    struct_logs: typing.Sequence[DebugTraceStructLog]


class DebugTraceStructLog(TypedDict):
    pc: int
    op: Opcode
    gas: int
    gas_cost: int
    depth: int
    stack: typing.Sequence[binary_types.PrefixHexData]
    memory: typing.Sequence[binary_types.RawHexData]


DebugBlockTrace = typing.Sequence[DebugTransactionTrace]

