"""
# Parameters for each query type

             1  2  3  4  5  6  7  8
───────────────────────────────────
   contract  ✓     ✓     ✓     ✓
     topic0  ✓  ✓        ✓  ✓
     topic1              ?  ?  ?  ?
     topic2              ?  ?  ?  ?
     topic3              ?  ?  ?  ?
start_block  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓
  end_block  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓
"""

import pytest

# from ctc.evm import event_utils_new as event_utils
from ctc.evm import event_utils


contract_address = '0x6b175474e89094c44da98b954eedeac495271d0f'
event_name = 'Transfer'
start_block = 14_200_000
end_block = 14_200_100

event_abi = {
    'anonymous': False,
    'inputs': [
        {
            'indexed': True,
            'internalType': 'address',
            'name': 'src',
            'type': 'address',
        },
        {
            'indexed': True,
            'internalType': 'address',
            'name': 'dst',
            'type': 'address',
        },
        {
            'indexed': False,
            'internalType': 'uint256',
            'name': 'wad',
            'type': 'uint256',
        },
    ],
    'name': 'Transfer',
    'type': 'event',
}


query_type_examples = [
    # 1
    (
        {
            'start_block': start_block,
            'end_block': end_block,
            'contract_address': contract_address,
            'event_abi': event_abi,
        },
        {
            'n_events': 62,
            'n_contracts': 1,
            'n_event_types': 1,
        },
    ),
    # 2
    (
        {
            'start_block': start_block,
            'end_block': end_block,
            'event_abi': event_abi,
        },
        {
            'n_events': 13645,
            'n_contracts': 1366,
            'n_event_types': 1,
        },
    ),
    # 3
    (
        {
            'start_block': start_block,
            'end_block': end_block,
            'contract_address': contract_address,
        },
        {
            'n_events': 69,
            'n_contracts': 1,
            'n_event_types': 2,
        },
    ),
    # 4
    (
        {
            'start_block': 14200001,
            'end_block': 14200001,
        },
        {
            'n_events': 25,
            'n_contracts': 10,
            'n_event_types': 5,
        },
    ),
    # 5
    (
        {
            'start_block': start_block,
            'end_block': end_block,
            'contract_address': contract_address,
            'event_abi': event_abi,
            'topic1': '0xa478c2975ab1ea89e8196811f51a7b7ade33eb11',
        },
        {
            'n_events': 5,
            'n_contracts': 1,
            'n_event_types': 1,
        },
    ),
    # 6
    (
        {
            'start_block': start_block,
            'end_block': end_block,
            'event_abi': event_abi,
            'topic1': '0xa478c2975ab1ea89e8196811f51a7b7ade33eb11',
        },
        {
            'n_events': 8,
            'n_contracts': 2,
            'n_event_types': 1,
        },
    ),
    # 7
    (
        {
            'start_block': start_block,
            'end_block': end_block,
            'contract_address': contract_address,
            'topic1': '0xa478c2975ab1ea89e8196811f51a7b7ade33eb11',
        },
        {
            'n_events': 5,
            'n_contracts': 1,
            'n_event_types': 1,
        },
    ),
]


@pytest.mark.parametrize('test', query_type_examples)
async def test_get_events_from_node(test):
    query, target_result = test
    actual_result = await event_utils.async_get_events(
        verbose=2,
        decode=False,
        context={'cache': False},
        **query,
    )

    assert len(actual_result) == target_result['n_events']
    assert (
        len(set(actual_result['contract_address']))
        == target_result['n_contracts']
    )
    assert (
        len(set(actual_result['event_hash'])) == target_result['n_event_types']
    )


@pytest.mark.parametrize('test', query_type_examples)
async def test_get_events_from_db(test):
    query, target_result = test
    actual_result = await event_utils.async_get_events(
        verbose=2,
        decode=False,
        context={'cache': True},
        **query,
    )

    assert len(actual_result) == target_result['n_events']
    assert (
        len(set(actual_result['contract_address']))
        == target_result['n_contracts']
    )
    assert (
        len(set(actual_result['event_hash'])) == target_result['n_event_types']
    )


@pytest.mark.parametrize('test', query_type_examples)
async def test_get_events_from_db_to_dict(test):
    query, target_result = test
    df = await event_utils.async_get_events(
        verbose=2,
        decode=False,
        context={'cache': True},
        **query,
    )
    actual_result = df.to_dicts()

    assert len(actual_result) == target_result['n_events']
    assert (
        len(set(event['contract_address'] for event in actual_result))
        == target_result['n_contracts']
    )
    assert (
        len(set(event['event_hash'] for event in actual_result))
        == target_result['n_event_types']
    )


@pytest.mark.parametrize('test', query_type_examples)
async def test_get_events_and_decode(test):
    query, target_result = test
    actual_result = await event_utils.async_get_events(
        verbose=2,
        decode=True,
        context={'cache': True},
        **query,
    )

    assert len(actual_result) == target_result['n_events']
    assert (
        len(set(actual_result['contract_address']))
        == target_result['n_contracts']
    )
    assert (
        len(set(actual_result['event_hash'])) == target_result['n_event_types']
    )


@pytest.mark.parametrize('test', query_type_examples)
async def test_get_events_and_decode_empty(test):
    query, target_result = test

    # change query to an empty block range
    target_result = dict(target_result)
    target_result['n_events'] = 0
    target_result['n_contracts'] = 0
    target_result['n_event_types'] = 0
    query = dict(query)
    query['start_block'] = 100
    query['end_block'] = 200

    actual_result = await event_utils.async_get_events(
        verbose=2,
        decode=True,
        context={'cache': True},
        **query,
    )

    assert len(actual_result) == target_result['n_events']
    assert (
        len(set(actual_result['contract_address']))
        == target_result['n_contracts']
    )
    assert (
        len(set(actual_result['event_hash'])) == target_result['n_event_types']
    )
