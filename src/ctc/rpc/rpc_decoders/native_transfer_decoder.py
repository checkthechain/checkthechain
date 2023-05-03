from __future__ import annotations

import typing

import msgspec


#
# # msgspec
#


CallAction = msgspec.defstruct(
    'CallAction',
    [
        ('from', typing.Optional[str], None),  # type: ignore
        ('to', typing.Optional[str], None),  # type: ignore
        ('value', typing.Optional[str], None),  # type: ignore
        ('author', typing.Optional[str], None),  # type: ignore
        ('address', typing.Optional[str], None),  # type: ignore
        ('refundAddress', typing.Optional[str], None),  # type: ignore
        ('balance', typing.Optional[str], None),  # type: ignore
    ],
    omit_defaults=True,
)

CallResult = msgspec.defstruct(
    'CallResult',
    [
        ('address', typing.Optional[str], None),  # type: ignore
    ],
    omit_defaults=True,
)


class CallTrace(msgspec.Struct, rename='camel'):
    type: str
    action: CallAction  # type: ignore
    subtraces: int
    trace_address: typing.Sequence[int]
    result: typing.Optional[CallResult] = None  # type: ignore
    error: typing.Union[str, None] = None


class TransactionReplay(msgspec.Struct, rename='camel'):
    transaction_hash: str
    trace: list[CallTrace]


class RpcResult(msgspec.Struct):
    result: list[TransactionReplay]


if typing.TYPE_CHECKING:
    from . import create_trace_decoder

    T = typing.TypeVar('T', CallTrace, create_trace_decoder.CreateTrace)


decoder = msgspec.json.Decoder(RpcResult)


def decode_native_transfers(
    responses: typing.Sequence[str],
    block_numbers: typing.Sequence[int],
) -> typing.Sequence[typing.Any]:
    blocks_replays = [decoder.decode(response).result for response in responses]

    # transform replays into eth transfers
    transfers = []
    for block_number, block_replay in zip(block_numbers, blocks_replays):
        transfer_index = 0
        for tx_replay in block_replay:
            for trace in filter_failed_traces(tx_replay.trace):
                transfer = native_transfer_from_call_trace(
                    trace=trace,
                    block_number=block_number,
                    transfer_index=transfer_index,
                    tx_hash=tx_replay.transaction_hash,
                )
                if transfer is not None:
                    transfers.append(transfer)
                    transfer_index += 1

    return transfers


def filter_failed_traces(traces: list[T]) -> list[T]:
    keep = []
    in_error = False
    error_address = None
    len_error_address = 0
    for t, trace in enumerate(traces):
        # restart fro each transaction
        if trace.trace_address == []:
            in_error = False
            error_address = None

        # if in an error, check if next trace is still in error
        if in_error:
            if (
                len(trace.trace_address) >= len_error_address
                and trace.trace_address[:len_error_address] == error_address
            ):
                keep.append(False)
                continue
            else:
                in_error = False
                error_address = None

        # check if current trace is start of an error
        if trace.error not in [None, '', 'None']:
            in_error = True
            error_address = trace.trace_address
            len_error_address = len(error_address)
            keep.append(False)
        else:
            keep.append(True)

    return [trace for trace, keep_trace in zip(traces, keep) if keep_trace]


def native_transfer_from_call_trace(
    *, trace: CallTrace, block_number: int, transfer_index: int, tx_hash: str
) -> typing.Sequence[typing.Any] | None:
    ttype = trace.type

    # parse value
    if ttype == 'suicide':
        value = trace.action.balance  # type: ignore
    else:
        value = trace.action.value  # type: ignore
    if value == '0x0':
        return None

    # parse from address and to address
    if ttype == 'reward':
        from_address = '0x0000000000000000000000000000000000000000'
        to_address = trace.action.author  # type: ignore
    elif ttype == 'create':
        if trace.result is None:
            return None
        from_address = getattr(trace.action, 'from')
        to_address = trace.result.address
    elif ttype == 'call':
        from_address = getattr(trace.action, 'from')
        to_address = trace.action.to  # type: ignore
    elif ttype == 'suicide':
        from_address = trace.action.address  # type: ignore
        to_address = trace.action.refundAddress  # type: ignore
    else:
        raise Exception(ttype)

    return [
        block_number,
        transfer_index,
        tx_hash,
        to_address,
        from_address,
        value,
    ]

