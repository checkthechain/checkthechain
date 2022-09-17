import pytest

from ctc import evm


example_domains = {
    '0x2901a982e363189e3f2e4db2e5c3291fa1067b815a3ac9890ac6573e51bf33b0': {
        'name': 'Aave Token',
        'version': '1',
        'chainId': 1,
        'verifyingContract': '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9',
    },
    '0x0ff37d1dc9a7d6539faa7634e8848d1d0bb7ec77e2bcb30d8982e62e6e2d5914': {
        'name': 'Fei USD',
        'version': '1',
        'chainId': 1,
        'verifyingContract': '0x956f47f50a910163d8bf957cf5846d573e7f87ca',
    },
}


@pytest.mark.parametrize('test', example_domains.items())
def test_get_domain_separator(test):
    target_domain_separator, domain = test
    actual_domain_separator = evm.get_domain_separator(domain)
    assert target_domain_separator == actual_domain_separator
