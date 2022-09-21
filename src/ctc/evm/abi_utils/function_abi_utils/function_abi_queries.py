from __future__ import annotations

import typing

from ctc import spec
from ... import binary_utils
from .. import contract_abi_utils
from . import function_abi_parsing


def get_function_abi(
    contract_abi: spec.ContractABI,
    function_name: typing.Optional[str] = None,
    *,
    n_parameters: typing.Optional[int] = None,
    parameter_types: typing.Optional[list[spec.ABIDatumType]] = None,
    function_selector: typing.Optional[spec.FunctionSelector] = None,
) -> spec.FunctionABI:
    """get function ABI from contract ABI"""

    if function_selector is not None:
        function_selector = binary_utils.binary_convert(
            function_selector, 'prefix_hex'
        )

    candidates = []
    for item in contract_abi:
        if item.get('type') != 'function':
            continue
        else:

            if typing.TYPE_CHECKING:
                function_abi = typing.cast(spec.FunctionABI, item)
            else:
                function_abi = item

        if (
            function_name is not None
            and function_abi.get('name') != function_name
        ):
            continue
        if (
            n_parameters is not None
            and len(function_abi['inputs']) != n_parameters
        ):
            continue
        if parameter_types is not None:
            types = function_abi_parsing.get_function_parameter_types(
                function_abi
            )
            if tuple(parameter_types) != tuple(types):
                continue
        if function_selector is not None:
            item_selector = function_abi_parsing.get_function_selector(
                function_abi
            )
            item_selector = binary_utils.binary_convert(item_selector, 'prefix_hex')
            if item_selector != function_selector:
                continue
        candidates.append(function_abi)

    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) == 0:
        raise LookupError('could not find function abi')
    elif len(candidates) > 0:
        import json

        as_json = [json.dumps(candidate) for candidate in candidates]
        if all(as_json[0] == entry for entry in as_json[1:]):
            return candidates[0]

        raise LookupError('too many candidates found for function abi')
    else:
        raise Exception('internal error')


async def async_get_function_abi(
    *,
    function_name: typing.Optional[str] = None,
    contract_abi: typing.Optional[spec.ContractABI] = None,
    contract_address: typing.Optional[spec.Address] = None,
    n_parameters: typing.Optional[int] = None,
    parameter_types: typing.Optional[list[spec.ABIDatumType]] = None,
    function_selector: typing.Optional[spec.FunctionSelector] = None,
    network: typing.Optional[spec.NetworkReference] = None,
) -> spec.FunctionABI:
    """get function ABI from local database or block explorer"""

    if contract_abi is None:
        if contract_address is None:
            raise Exception('must specify contract_abi or contract_address')
        contract_abi = await contract_abi_utils.async_get_contract_abi(
            contract_address=contract_address,
            network=network,
        )

    try:
        return get_function_abi(
            function_name=function_name,
            contract_abi=contract_abi,
            n_parameters=n_parameters,
            parameter_types=parameter_types,
            function_selector=function_selector,
        )

    except LookupError as e:

        # query contract_abi again if contract abi might have changed since db
        if contract_address is not None:
            contract_abi = await contract_abi_utils.async_get_contract_abi(
                contract_address=contract_address,
                network=network,
                db_query=False,
            )

            return get_function_abi(
                function_name=function_name,
                contract_abi=contract_abi,
                n_parameters=n_parameters,
                parameter_types=parameter_types,
                function_selector=function_selector,
            )

        else:
            raise e


def get_function_abis(
    contract_abi: spec.ContractABI,
) -> typing.Sequence[spec.FunctionABI]:
    """get list of function ABI's in contract ABI"""
    return [item for item in contract_abi if item['type'] == 'function']
