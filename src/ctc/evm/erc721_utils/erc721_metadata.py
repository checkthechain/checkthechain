from __future__ import annotations

from ctc import spec
from .. import abi_utils


async def async_is_erc721(
    contract_address: spec.Address | None,
    *,
    contract_abi: spec.ContractABI | None = None,
    context: spec.Context = None,
) -> bool:
    """return whether contract at address implements erc721 standard"""

    if contract_abi is None:
        if contract_address is None:
            raise Exception('specify either contract_address or contract_abi')
        contract_abi = await abi_utils.async_get_contract_abi(
            contract_address, context=context
        )

    return _is_erc721_contract_abi(contract_abi)


def _is_erc721_contract_abi(contract_abi: spec.ContractABI) -> bool:
    """return whether contract abi implements erc721 standard"""

    erc721_signatures = {
        #
        # function signatures
        'balanceOf(address)',
        'ownerOf(uint256)',
        'safeTransferFrom(address,address,uint256,bytes)',
        'safeTransferFrom(address,address,uint256)',
        'transferFrom(address,address,uint256)',
        'approve(address,uint256)',
        'setApprovalForAll(address,bool)',
        'getApproved(uint256)',
        'isApprovedForAll(address,address)',
        #
        # event signatures
        'Transfer(address,address,uint256)',
        'Approval(address,address,uint256)',
        'ApprovalForAll(address,address,bool)',
    }

    contract_signatures = set()
    for item in contract_abi:
        if item.get('type') == 'function':
            signature = abi_utils.get_function_signature(function_abi=item)  # type: ignore
            contract_signatures.add(signature)
        elif item.get('type') == 'event':
            signature = abi_utils.get_event_signature(event_abi=item)  # type: ignore
            contract_signatures.add(signature)

    missing_signatures = erc721_signatures - contract_signatures

    return len(missing_signatures) == 0

