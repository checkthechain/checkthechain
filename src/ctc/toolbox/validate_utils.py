import numpy as np


def _ensure_exactly_one(*args):
    non_none = list(arg for arg in args if arg is not None)
    if len(non_none) > 1:
        raise Exception('too many arguments specified')
    if len(non_none) == 0:
        raise Exception('not enough arguments specified')
    return non_none[0]


def _ensure_positive(value, error=True):
    if isinstance(value, (np.ndarray, tuple, list)):
        positive = all(subvalue > 0 for subvalue in value)
    else:
        positive = value > 0

    if error and not positive:
        raise Exception('value must be positive')

    return positive


def _ensure_non_negative(value, error=True):
    if isinstance(value, (np.ndarray, tuple, list)):
        non_negative = all(
            subvalue >= 0 or np.isclose(subvalue, 0, atol=1e-7) for subvalue in value
        )
    else:
        non_negative = value >= 0 or np.isclose(value, 0, atol=1e-7)

    if error and not non_negative:
        raise Exception('value must be non negative')

    return non_negative


def _ensure_values_equal(lhs, rhs):
    if isinstance(lhs, dict):
        assert set(lhs.keys()) == set(rhs.keys())
        for key in lhs.keys():
            _ensure_values_equal(lhs[key], rhs[key])
    else:
        assert np.isclose(lhs, rhs)

