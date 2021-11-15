from ctc.protocols import balancer_utils


def test_get_pool_id():
    pool_id = balancer_utils.get_pool_id('0xede4efcc5492cf41ed3f0109d60bc0543cfad23a')
    assert pool_id == '0xede4efcc5492cf41ed3f0109d60bc0543cfad23a0002000000000000000000bb'


def test_get_pool_address():
    pool_address = balancer_utils.get_pool_address('0xede4efcc5492cf41ed3f0109d60bc0543cfad23a0002000000000000000000bb')
    assert pool_address == '0xede4efcc5492cf41ed3f0109d60bc0543cfad23a'


def test_get_pool_swaps():
    pool_address = '0xede4efcc5492cf41ed3f0109d60bc0543cfad23a'
    swaps = balancer_utils.get_pool_swaps(pool_address=pool_address, end_block=13613577)
    assert len(swaps) == 5

