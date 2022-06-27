"""
## Resources
- https://github.com/TokenEngineeringCommunity/BalancerPools_Model
- https://token-engineering-balancer.gitbook.io/balancer-simulations/additional-code-and-instructions/balancer-the-python-edition/balancer_math.py
"""

from __future__ import annotations

from ctc import spec


def calc_out_given_in(
    *,
    token_amount_in: spec.Number,
    token_balance_in: spec.Number,
    token_weight_in: float,
    token_balance_out: spec.Number,
    token_weight_out: float,
    swap_fee: float,
) -> spec.Number:
    """
    adapted from https://github.com/TokenEngineeringCommunity/BalancerPools_Model
    """
    weight_ratio = token_weight_in / token_weight_out
    adjusted_in = token_amount_in * (1 - swap_fee)
    y = token_balance_in / (token_balance_in + adjusted_in)
    foo = pow(y, weight_ratio)
    bar = 1 - foo
    token_amount_out = token_balance_out * bar
    if not spec.is_number(token_amount_out):
        raise Exception('cannot compute result')
    return token_amount_out
