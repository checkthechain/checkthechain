from ctc import evm


def test_fetch_latest_block():
    latest_block = evm.fetch_latest_block()
    assert latest_block is not None


def test_fetch_latest_block_number():
    latest_block_number = evm.fetch_latest_block_number()
    assert isinstance(latest_block_number, int)


@evm.parallelize_block_fetching()
def get_token_total_supply(block):
    fei_address = '0x956F47F50A910163D8BF957Cf5846D573E7f87CA'
    return evm.fetch_token_total_supply(
        token=fei_address,
        block=block,
        normalize=False,
    )


def test_paralllelize_block_fetching():
    results = get_token_total_supply(blocks=[13430000, 13420000, 13410000])
    assert tuple(results) == (
        523898681781993861958312785,
        525899964299071436994307742,
        536187038961679805771891134,
    )

