import pytest
import numpy as np

from ctc.toolbox.defi_utils.dex_utils.amm_utils import cpmm
from ctc.toolbox import validate_utils


x_reserves = 1e6
y_reserves = 1e3


@pytest.mark.parametrize('x_sold', [1e1, 1e6, 1e10])
def test_trade_x_sold(x_sold):

    result = cpmm.trade(
        x_reserves=x_reserves,
        y_reserves=y_reserves,
        x_sold=x_sold,
    )

    assert result['new_pool']['x_reserves'] == x_reserves + x_sold
    assert result['new_pool']['y_reserves'] == y_reserves - result['y_bought']
    assert result['y_bought'] == cpmm.compute_y_bought_when_x_sold(
        x_sold=x_sold,
        x_reserves=x_reserves,
        y_reserves=y_reserves,
    )


@pytest.mark.parametrize('y_sold', [1e1, 1e6, 1e10])
def test_trade_y_sold(y_sold):

    result = cpmm.trade(
        x_reserves=x_reserves,
        y_reserves=y_reserves,
        y_sold=y_sold,
    )

    assert result['new_pool']['x_reserves'] == x_reserves - result['x_bought']
    assert result['new_pool']['y_reserves'] == y_reserves + y_sold
    assert result['x_bought'] == cpmm.compute_y_bought_when_x_sold(
        x_sold=y_sold,
        x_reserves=y_reserves,
        y_reserves=x_reserves,
    )


@pytest.mark.parametrize('x_bought', [1e1, 1e3, 1e5])
def test_trade_x_bought(x_bought):

    result = cpmm.trade(
        x_reserves=x_reserves,
        y_reserves=y_reserves,
        x_bought=x_bought,
    )
    assert result['new_pool']['x_reserves'] == x_reserves - x_bought
    assert result['new_pool']['y_reserves'] == y_reserves + result['y_sold']

    # ensure that the reserve specification gives the same result
    reverse_result = cpmm.trade(
        x_reserves=x_reserves,
        y_reserves=y_reserves,
        y_sold=result['y_sold'],
    )
    validate_utils._ensure_values_equal(result, reverse_result)


@pytest.mark.parametrize('y_bought', [1e0, 1e1, 1e2])
def test_trade_y_bought(y_bought):

    result = cpmm.trade(
        x_reserves=x_reserves,
        y_reserves=y_reserves,
        y_bought=y_bought,
    )
    assert result['new_pool']['x_reserves'] == x_reserves - result['x_bought']
    assert result['new_pool']['y_reserves'] == y_reserves - y_bought

    # ensure that the reserve specification gives the same result
    reverse_result = cpmm.trade(
        x_reserves=x_reserves,
        y_reserves=y_reserves,
        x_sold=result['x_sold'],
    )
    validate_utils._ensure_values_equal(result, reverse_result)


@pytest.mark.parametrize('new_x_reserves', [1e1, 1e6, 1e9])
def test_trade_new_x_reserves(new_x_reserves):

    result = cpmm.trade_to_target_reserves(
        x_reserves=x_reserves,
        y_reserves=y_reserves,
        new_x_reserves=new_x_reserves,
    )
    assert result['new_pool']['x_reserves'] == new_x_reserves

    # ensure that the resulting trade produces the same results
    count = 0
    for name in ['x_sold', 'y_sold', 'y_bought', 'x_bought']:
        if result[name] >= 0:
            reverse_result = cpmm.trade(
                x_reserves=x_reserves,
                y_reserves=y_reserves,
                **{name: result[name]},
            )
            validate_utils._ensure_values_equal(result, reverse_result)
            count += 1
    if count < 2:
        raise Exception('could not detect enough suitable reverse trades')


@pytest.mark.parametrize('new_y_reserves', [1e1, 1e3, 1e6])
def test_trade_y_reserves_new(new_y_reserves):

    result = cpmm.trade_to_target_reserves(
        x_reserves=x_reserves,
        y_reserves=y_reserves,
        new_y_reserves=new_y_reserves,
    )
    assert result['new_pool']['y_reserves'] == new_y_reserves

    # ensure that the resulting trade produces the same results
    count = 0
    for name in ['x_sold', 'y_sold', 'y_bought', 'x_bought']:
        if result[name] >= 0:
            reverse_result = cpmm.trade(
                x_reserves=x_reserves,
                y_reserves=y_reserves,
                **{name: result[name]},
            )
            validate_utils._ensure_values_equal(result, reverse_result)
            count += 1
    if count < 2:
        raise Exception('could not detect enough suitable reverse trades')


@pytest.mark.parametrize('new_price', [1e-8, 1e-2, 1e2, 1e8])
def test_trade_to_price(new_price):

    # modify x per y
    result = cpmm.trade_to_price(
        x_reserves=x_reserves,
        y_reserves=y_reserves,
        new_x_per_y=new_price,
    )
    result_price = (
        result['new_pool']['x_reserves'] / result['new_pool']['y_reserves']
    )
    assert np.isclose(new_price, result_price)

    # modify y per x
    result = cpmm.trade_to_price(
        x_reserves=x_reserves,
        y_reserves=y_reserves,
        new_y_per_x=new_price,
    )
    result_price = (
        result['new_pool']['y_reserves'] / result['new_pool']['x_reserves']
    )
    assert np.isclose(new_price, result_price)


def test_reject_negative_values():
    for arg in [
        'x_sold',
        'y_sold',
        'x_bought',
        'y_bought',
    ]:
        with pytest.raises(Exception):
            cpmm.trade(
                x_reserves=x_reserves, y_reserves=y_reserves, **{arg: -1}
            )
