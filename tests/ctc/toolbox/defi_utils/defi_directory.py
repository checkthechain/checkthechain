import pytest

from ctc.toolbox.defi_utils import dex_utils


dexes = [
    'Balancer',
    'Curve',
    'Sushi',
    'Uniswap V2',
    'Uniswap V3',
]


@pytest.mark.parametrize('dex_name', dexes)
@pytest.mark.parametrize('network', [1])
def test_dex_directory_matches_classes(dex_name, network):

    dex = dex_utils.get_dex(dex_name)
    dex_factories = set(dex.get_pool_factories(network))

    dex_names_of_factories = dex_utils.get_dex_names_of_factories(
        network=network
    )
    directory_factories = set(
        factory
        for factory, other_dex_name in dex_names_of_factories.items()
        if other_dex_name == dex_name
    )

    assert directory_factories == dex_factories
