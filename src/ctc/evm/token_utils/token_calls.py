from ctc.toolbox import web3_utils
from .. import contract_abi_utils
from .. import token_utils


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


def _get_web3_token_contract(token=None, abi=None, **contract_kwargs):

    if abi is None:
        abi = 'ERC20'

    return web3_utils.get_web3_contract(
        contract_address=token_utils.get_token_address(token),
        contract_abi=contract_abi_utils.load_named_contract_abi(contract_name=abi),
        **contract_kwargs
    )


