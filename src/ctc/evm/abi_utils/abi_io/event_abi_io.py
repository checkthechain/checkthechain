import typing

from ctc import binary
from ctc import spec
from . import contract_abi_io


async def async_get_event_abi(
    contract_abi: typing.Optional[spec.ContractABI] = None,
    contract_address: typing.Optional[spec.Address] = None,
    event_name: typing.Optional[str] = None,
    event_hash: typing.Optional[str] = None,
    event_abi: typing.Optional[spec.EventABI] = None,
    network: typing.Optional[spec.NetworkReference] = None,
):

    # get contract abi
    if contract_abi is None:
        contract_abi = await contract_abi_io.async_get_contract_abi(
            contract_address=contract_address,
            network=network,
        )

    return binary.get_event_abi(
        contract_abi=contract_abi,
        event_name=event_name,
        event_hash=event_hash,
        event_abi=event_abi,
    )

