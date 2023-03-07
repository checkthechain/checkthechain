from __future__ import annotations

import typing

import msgspec


class Log(msgspec.Struct, rename='camel'):
    block_number: str
    transaction_index: str
    log_index: str
    transaction_hash: str
    address: str
    topics: tuple[str, ...]
    data: str
    removed: bool
    block_hash: str


class RpcResult(msgspec.Struct):
    result: list[Log]


decoder = msgspec.json.Decoder(RpcResult)


def decode_logs(
    raw_response: str,
    include_removed: bool = False,
) -> typing.Sequence[tuple[int, int, int, str, str, tuple[str, ...], str, str]]:

    response = decoder.decode(raw_response)
    logs = response.result

    return [
        (
            int(log.block_number, 16),
            int(log.transaction_index, 16),
            int(log.log_index, 16),
            log.transaction_hash,
            log.address,
            log.topics,
            log.data,
            log.block_hash,
        )
        for log in logs
        if (not log.removed or include_removed)
    ]

