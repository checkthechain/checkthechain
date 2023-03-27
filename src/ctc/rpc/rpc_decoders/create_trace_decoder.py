from __future__ import annotations

import typing

import msgspec


#
# # msgspec
#

CreateAction = msgspec.defstruct(
    'CreateAction',
    [
        ('from', typing.Optional[str], None),  # type: ignore
        ('init', typing.Optional[str], None),  # type: ignore
    ],
    omit_defaults=True,
)

CreateResult = msgspec.defstruct(
    'CreateResult',
    [
        ('address', typing.Optional[str], None),  # type: ignore
        ('code', typing.Optional[str], None),  # type: ignore
    ],
)


class CreateTrace(msgspec.Struct, omit_defaults=True, rename='camel'):
    type: str
    trace_address: list[int]
    subtraces: int
    action: typing.Optional[CreateAction] = None  # type: ignore
    result: typing.Optional[CreateResult] = None  # type: ignore
    transaction_hash: typing.Optional[str] = None
    error: typing.Optional[str] = None


class RpcResult(msgspec.Struct):
    result: list[CreateTrace]


decoder = msgspec.json.Decoder(RpcResult)


#
# # functions
#


def decode_create_traces(raw_block_trace: str, block_number: int) -> typing.Sequence[CreateTrace]:

    response = decoder.decode(raw_block_trace)
    call_traces = response.result

    from . import native_transfer_decoder
    call_traces = native_transfer_decoder.filter_failed_traces(call_traces)

    create_traces: list[CreateTrace] = []
    for t, trace in enumerate(call_traces):
        if trace.type == 'create' and trace.result is not None:

            # identify root trace for deployer
            d = t
            while call_traces[d].trace_address != []:
                d = d - 1
                if d < 0:
                    raise Exception('could not find deployer of trace')

            # create trace
            create_trace = {
                'block_number': block_number,
                'create_index': len(create_traces),
                'transaction_hash': trace.transaction_hash,
                'contract_address': trace.result.address,
                'deployer': getattr(call_traces[d].action, 'from'),
                'factory': getattr(trace.action, 'from'),
                'init_code': trace.action.init,
                'code': trace.result.code,
            }

            create_traces.append(create_trace)

    return create_traces

