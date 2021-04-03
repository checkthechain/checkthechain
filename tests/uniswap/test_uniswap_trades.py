import pytest

from fei.toolbox import uniswap_utils


# lhs_pool rhs_pool trade_amount receive_amount
trades = [
    [1000, 1000, 500, (333 + 1 / 3)],
]


@pytest.mark.parametrize('trade', trades)
def test_uniswap_trade(trade):
    lhs_pool, rhs_pool, trade_amount, receive_amount = trade

    output = uniswap_utils.trade_x_for_y(
        x_pool=lhs_pool, y_pool=rhs_pool, x_amount=trade_amount, fee=0,
    )

    assert output == receive_amount

