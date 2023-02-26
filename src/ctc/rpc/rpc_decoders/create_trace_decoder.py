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
    action: typing.Optional[CreateAction] = None  # type: ignore
    result: typing.Optional[CreateResult] = None  # type: ignore
    transaction_hash: typing.Optional[str] = None


class RpcResult(msgspec.Struct):
    result: list[CreateTrace]


decoder = msgspec.json.Decoder(RpcResult)


#
# # functions
#


def decode_create_traces(raw_block_trace: str) -> typing.Sequence[CreateTrace]:

    response = decoder.decode(raw_block_trace)
    call_traces = response.result

    create_traces: list[CreateTrace] = []
    for t, trace in enumerate(call_traces):
        if trace.type == 'create' and trace.result is not None:
            create_trace = {
                'transaction_hash': trace.transaction_hash,
                'contract_address': trace.result.address,
                'from': getattr(trace.action, 'from'),
                'init_code': trace.action.init,
                'code': trace.result.code,
            }

            d = t
            while call_traces[d].trace_address != []:
                d = d - 1
                if d < 0:
                    raise Exception('could not find deployer of trace')
            create_trace['deployer'] = getattr(call_traces[d].action, 'from')
            create_traces.append(create_trace)
    return create_traces

