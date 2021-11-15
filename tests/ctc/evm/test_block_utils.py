from ctc import evm


def test_get_block():
    latest_block = evm.get_block('latest')
    assert latest_block is not None


def test_fetch_latest_block_number():
    latest_block_number = evm.get_block_number('latest')
    assert isinstance(latest_block_number, int)


@evm.parallelize_block_fetching()
def get_token_total_supply(block):
    """this is a helper function for the parallelize test below"""
    fei_address = '0x956F47F50A910163D8BF957Cf5846D573E7f87CA'
    return evm.get_erc20_total_supply(
        token=fei_address,
        block=block,
        normalize=False,
    )


def test_parallelize_block_fetching():
    results = get_token_total_supply(blocks=[13430000, 13420000, 13410000])
    assert tuple(results) == (
        523898681781993861958312785,
        525899964299071436994307742,
        536187038961679805771891134,
    )


def test_get_contract_creation_block():
    contract = '0x6B175474E89094C44Da98b954EedeAC495271d0F'
    result = evm.get_contract_creation_block(contract)
    target = 8928158
    assert result == target

