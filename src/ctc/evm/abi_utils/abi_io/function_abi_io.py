from __future__ import annotations

import typing

from ctc import binary
from ctc import spec
from . import contract_abi_io


async def async_get_function_abi(
    function_name: typing.Optional[str] = None,
    contract_abi: typing.Optional[spec.ContractABI] = None,
    contract_address: typing.Optional[spec.Address] = None,
    n_parameters: typing.Optional[int] = None,
    parameter_types: typing.Optional[list[spec.ABIDatumType]] = None,
    function_selector: typing.Optional[spec.FunctionSelector] = None,
    network: typing.Optional[spec.NetworkReference] = None,
) -> spec.FunctionABI:

    if contract_abi is None:
        contract_abi = await contract_abi_io.async_get_contract_abi(
            contract_address=contract_address,
            network=network,
        )

    return binary.get_function_abi(
        function_name=function_name,
        contract_abi=contract_abi,
        n_parameters=n_parameters,
        parameter_types=parameter_types,
        function_selector=function_selector,
    )

