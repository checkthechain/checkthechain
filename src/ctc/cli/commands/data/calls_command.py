import pandas as pd

from ctc import binary
from ctc import evm
from ctc import rpc
from ctc.cli import cli_utils


def get_command_spec():
    return {
        'f': async_calls_command,
        'args': [
            {'name': 'args', 'kwargs': {'nargs': '*'}},
            {'name': '--to-addresses', 'kwargs': {'nargs': '+'}},
            {'name': '--blocks', 'kwargs': {'nargs': '+'}},
            {'name': '--block', 'kwargs': {}},
            {'name': '--quiet', 'kwargs': {'action': 'store_true'}},
            {'name': '--output', 'kwargs': {'default': 'stdout'}},
            {'name': '--overwrite', 'kwargs': {'action': 'store_true'}},
        ],
    }


async def async_calls_command(
    args, to_addresses, blocks, block, quiet, output, overwrite
):

    if blocks is not None and to_addresses is not None:
        raise Exception('cannot specify both --blocks or --to-addresses')
    if blocks is None and to_addresses is None:
        raise Exception('must specify either --blocks or --to-addresses')

    if blocks is not None:
        if block is not None:
            raise Exception('cannot specify both --block and --blocks')

        to_address, function_name, *function_parameters = args

        block_numbers = await cli_utils.async_resolve_blocks(blocks)

        # fetch data
        results = await rpc.async_batch_eth_call(
            to_address=to_address,
            function_name=function_name,
            function_parameters=function_parameters,
            block_numbers=block_numbers,
        )

        # get output names
        function_abi = await evm.async_get_function_abi(
            contract_address=to_address,
            function_name=function_name,
        )
        output_names = binary.get_function_output_names(
            function_abi, human_readable=True
        )

        # format into dataframe
        df = pd.DataFrame(results, index=block_numbers)
        df.index.name = 'block'
        df.columns = output_names

    elif to_addresses is not None:
        if block is None:
            block = 'latest'

        function_name, *function_parameters = args

        # assert that all address functions have the same number of outputs
        function_abi = await evm.async_get_function_abi(
            contract_address=to_addresses[0],
            function_name=function_name,
        )
        n_outputs = len(function_abi['outputs'])
        for to_address in to_addresses[1:]:
            other_function_abi = await evm.async_get_function_abi(
                contract_address=to_address,
                function_name=function_name,
            )
            if len(other_function_abi['outputs']) != n_outputs:
                print('to-addresses do no have same number of function outputs')

        # fetch data
        results = await rpc.async_batch_eth_call(
            to_addresses=to_addresses,
            function_name=function_name,
            function_parameters=function_parameters,
            block_number=block,
        )

        # name based on first contract's abi
        output_names = binary.get_function_output_names(
            function_abi, human_readable=True
        )

        df = pd.DataFrame(results, index=to_addresses)
        df.index.name = 'to_address'
        df.columns = output_names

    else:
        raise Exception('must specify either --blocks or --to-addresses')

    cli_utils.output_data(data=df, output=output, overwrite=overwrite)

    await rpc.async_close_http_session()

