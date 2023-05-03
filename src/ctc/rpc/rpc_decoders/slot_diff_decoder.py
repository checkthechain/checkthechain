from __future__ import annotations

import typing

import msgspec

if typing.TYPE_CHECKING:
    SlotsData = typing.MutableMapping[
        tuple[str, str], typing.MutableMapping[str, typing.Any]
    ]


# SlotChanges = msgspec.defstruct(
#     'SlotChanges',
#     [
#         ('+', typing.Optional, None),
#         ('*', typing.Optional, None),
#         ('-', typing.Optional, None),
#     ],
#     omit_defaults=True,
# )

SlotAddress = str
ChangeType = str
SlotChanges = typing.Mapping[
    ChangeType, typing.Union[str, typing.Mapping[str, str]]
]


class ContractStateDiff(msgspec.Struct):
    storage: typing.Mapping[SlotAddress, SlotChanges]


class TraceResult(msgspec.Struct, rename='camel'):
    state_diff: typing.Mapping[str, ContractStateDiff]


class RpcResult(msgspec.Struct):
    result: list[TraceResult]


decoder = msgspec.json.Decoder(RpcResult)


def decode_slot_stats(
    raw_responses: typing.Sequence[str],
    block_numbers: typing.Sequence[int],
) -> SlotsData:
    slots_data: SlotsData = {}

    for raw_response, block_number in zip(raw_responses, block_numbers):
        response = decoder.decode(raw_response)
        for trace_result in response.result:
            for contract_address, state_diff in trace_result.state_diff.items():
                for slot, slot_changes in state_diff.storage.items():
                    key = (contract_address, slot)

                    # initialize slot
                    if key not in slots_data:
                        _initialize_slot(
                            slots_data=slots_data,
                            key=key,
                            slot_changes=slot_changes,
                            block_number=block_number,
                        )
                    else:
                        _integrate_slot_changes(
                            slots_data=slots_data,
                            key=key,
                            slot_changes=slot_changes,
                            block_number=block_number,
                        )

    return slots_data


def _initialize_slot(
    *,
    slots_data: SlotsData,
    key: tuple[str, str],
    slot_changes: typing.Mapping[str, typing.Any],
    block_number: int,
) -> None:
    if '+' in slot_changes:
        slots_data[key] = {
            'first_nonzero_block': block_number,
            'last_updated_block': block_number,
            'last_zero_block': None,
            'n_tx_updates': 1,
            'value': slot_changes['+'],
        }
    elif '*' in slot_changes:
        slots_data[key] = {
            'first_nonzero_block': block_number,
            'last_updated_block': block_number,
            'last_zero_block': None,
            'n_tx_updates': 1,
            'value': slot_changes['*']['to'],
        }
    elif '-' in slot_changes:
        slots_data[key] = {
            'first_nonzero_block': None,
            'last_updated_block': block_number,
            'last_zero_block': block_number,
            'n_tx_updates': 1,
            'value': '0x0',
        }
        raise Exception()
    else:
        raise Exception('unknown slot changes')


def _integrate_slot_changes(
    *,
    slots_data: SlotsData,
    key: tuple[str, str],
    slot_changes: typing.Mapping[str, typing.Any],
    block_number: int,
) -> None:
    """this function should be called for each block in increasing order"""

    datum = slots_data[key]
    datum['n_tx_updates'] += 1

    if '+' in slot_changes:
        datum['last_updated_block'] = block_number
        datum['value'] = slot_changes['+']
    elif '*' in slot_changes:
        datum['last_updated_block'] = block_number
        datum['value'] = slot_changes['*']['to']
    elif '-' in slot_changes:
        datum['last_zero_block'] = block_number
        datum['last_updated_block'] = block_number
        datum['value'] = '0x0'
    else:
        raise Exception('unknown slot changes')


#
# # flatten slot stats
#


def flatten_slots_data(
    slots_data: typing.Mapping[tuple[str, str], typing.Mapping[str, typing.Any]]
) -> typing.Sequence[typing.Mapping[str, typing.Any]]:
    return [
        dict(slot_data, contract_address=contract_address, slot=slot)
        for (contract_address, slot), slot_data in slots_data.items()
    ]


#
# # combining multiple slot datas
#


# def combine_slots_data(
#     slots_data_list: typing.Sequence[SlotsData],
# ) -> SlotsData:
#     if len(slots_data_list):
#         return {}
#     else:
#         slots_data: SlotsData = dict(slots_data_list[0])
#         for other_slots_data in slots_data_list[1:]:
#             for slot_address, other_slot_data in other_slots_data.items():
#                 _combine_slot_data(
#                     slots_data=slots_data,
#                     slot_address=slot_address,
#                     other_slot_data=other_slot_data,
#                 )
#     return slots_data


# def _combine_slot_data(
#     slots_data: SlotsData,
#     slot_address: tuple[str, str],
#     other_slot_data: typing.MutableMapping[str, typing.Any],
# ) -> None:
#     if slot_address not in slots_data:
#         slots_data[slot_address] = other_slot_data
#     else:
#         slot_data = slots_data[slot_address]

#         slots_data['n_tx_updates'] += other_slot_data['n_tx_updates']

#         if other_slot_data['first_nonzero_block'] is not None:
#             if slot_data['first_nonzero_block'] is None:
#                 slot_data['first_nonzero_block'] = other_slot_data[
#                     'first_nonzero_block'
#                 ]
#             elif (
#                 other_slot_data['first_nonzero_block']
#                 < slot_data['first_nonzero_block']
#             ):
#                 slot_data['first_nonzero_block'] = other_slot_data[
#                     'first_nonzero_block'
#                 ]

#         if other_slot_data['last_nonzero_block'] is not None:
#             if slot_data['last_nonzero_block'] is None:
#                 slot_data['last_nonzero_block'] = other_slot_data[
#                     'last_nonzero_block'
#                 ]
#             elif (
#                 other_slot_data['last_nonzero_block']
#                 > slot_data['last_nonzero_block']
#             ):
#                 slot_data['last_nonzero_block'] = other_slot_data[
#                     'last_nonzero_block'
#                 ]

#         if slot_data['last_updated_block'] is None:
#             slot_data['last_updated_block'] = other_slot_data[
#                 'last_updated_block'
#             ]
#         elif (
#             other_slot_data['last_updated_block']
#             > slot_data['last_updated_block']
#         ):
#             slot_data['last_updated_block'] = other_slot_data[
#                 'last_updated_block'
#             ]

