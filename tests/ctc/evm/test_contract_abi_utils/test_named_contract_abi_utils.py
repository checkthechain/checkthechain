import os

from ctc import evm
from ctc import config_utils


def test_get_named_contract_abi_root():
    root = evm.get_named_contract_abi_root()

    config = config_utils.get_config()
    target_root = os.path.join(config['evm_root'], 'named_contract_abis')

    assert root == target_root


def test_load_named_contract_abi():
    result = evm.load_named_contract_abi(
        contract_name='Core',
        project='fei',
    )
    assert len(result) == 49


def test_load_abi_by_name():
    result = evm.load_abi_by_name(
        contract_name='Core',
        project='fei',
    )
    assert len(result) == 49


def test_load_contract_metadata():
    result = evm.load_contract_metadata(
        contract_address='0x8d5ED43dCa8C2F7dFB20CF7b53CC7E593635d7b9'.lower(),
    )
    assert result['common_name'] == 'Core'
    assert result['contract_name'] == 'Core'
    assert result['project'] == 'fei'


def test_load_named_abi_by_address():
    abi = evm.load_named_abi_by_address(
        contract_address='0x8d5ED43dCa8C2F7dFB20CF7b53CC7E593635d7b9'.lower(),
    )
    assert len(abi) == 49

