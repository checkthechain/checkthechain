from ctc import directory
from ctc.toolbox import web3_utils
from .. import address_utils
from .. import contract_abi_utils


def call_token_contract(
    function,
    token=None,
    contract=None,
    block=None,
    args=None,
    **contract_kwargs
):
    # use web3 for now

    if contract is None:
        contract = _get_web3_token_contract(token=token, **contract_kwargs)

    return web3_utils.call_web3_contract(
        contract=contract,
        function=function,
        args=args,
        block=block,
    )


def _get_web3_token_contract(
    token=None, contract_address=None, contract_abi=None, **contract_kwargs
):

    if token is not None and contract_address is None:
        if not address_utils.is_address_str(token):
            contract_address = directory.token_addresses[token.lower()]
        else:
            contract_address = token

    if contract_abi is None:
        contract_abi = contract_abi_utils.get_contract_abi(
            contract_address=contract_address
        )

    return web3_utils.get_web3_contract(
        contract_address=contract_address,
        contract_abi=contract_abi,
        **contract_kwargs
    )

