"""WIP"""
from __future__ import annotations

import typing
import functools

import pandas as pd

from ctc import evm
from ctc import spec
from .. import binary_utils


async def async_get_transaction_traces_df(
    transaction_hash: spec.PrefixHexData,
    provider: spec.ProviderReference = None,
) -> spec.DataFrame:

    from ctc.rpc.rpc_executors import rpc_trace_executors

    traces = await rpc_trace_executors.async_trace_transaction(
        transaction_hash=transaction_hash,
    )

    data: dict[str, list[typing.Any]] = {}

    for trace in traces:
        for key, value in trace.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    full_key = key + '__' + subkey
                    data.setdefault(full_key, [])
                    data[full_key].append(subvalue)
            else:
                data.setdefault(key, [])
                data[key].append(value)

    df = pd.DataFrame(data)

    # convert columns to int
    convert_int_columns = [
        'action__gas',
        'result__gasUsed',
        'action__value',
    ]
    f_to_int = functools.partial(
        binary_utils.binary_convert, output_format='integer'
    )
    for column in convert_int_columns:
        df[column] = df[column].map(f_to_int)

    # remove redundant columns
    remove_columns = [
        'transactionHash',
        'transactionPosition',
        'blockNumber',
        'blockHash',
    ]
    df = df.drop(remove_columns, axis=1)

    # decode call data and parameters
    await _async_add_trace_call_data(df)

    return df


async def _async_add_trace_call_data(df: spec.DataFrame) -> None:

    contract_abis = {}
    for contract_address in set(df['action__to']):
        contract_abis[contract_address] = await evm.async_get_contract_abi(
            contract_address=contract_address,
        )

    action_call_data: dict[str, list[typing.Any]] = {
        'action__name': [],
        'action__parameters': [],
        'result__outputs': [],
    }

    for action_to, action_input, result__output in zip(
        df['action__to'], df['action__input'], df['result__output']
    ):

        if action_input == '0x':
            action_call_data['action__name'].append('')
            action_call_data['action__parameters'].append(tuple())
            action_call_data['result__outputs'].append(None)

        else:

            try:

                decoded = evm.decode_call_data(
                    contract_abi=contract_abis[action_to],
                    call_data=action_input,
                )
                action_call_data['action__name'].append(
                    decoded['function_abi']['name']
                )
                action_call_data['action__parameters'].append(
                    decoded['parameters']
                )

                function_abi = evm.get_function_abi(
                    contract_abi=contract_abis[action_to],
                    function_selector=action_input[:10],
                )
                result__outputs = evm.decode_function_output(
                    encoded_output=result__output,
                    function_abi=function_abi,
                )
                action_call_data['result__outputs'].append(result__outputs)

            except LookupError:

                action_call_data['action__name'].append('UNKNOWN')
                action_call_data['action__parameters'].append('UNKNOWN')
                action_call_data['result__outputs'].append('UNKNOWN')

    df['action__name'] = action_call_data['action__name']
    df['action__parameters'] = action_call_data['action__parameters']
    df['result__outputs'] = action_call_data['result__outputs']
