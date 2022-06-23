from ctc.config import config_defaults


def test_default_networks_have_unique_names():
    network_names_by_chain_id = (
        config_defaults.get_default_network_names_by_chain_id()
    )
    assert len(network_names_by_chain_id) == len(
        set(network_names_by_chain_id.values())
    )


def test_all_default_networks_have_block_explorers():
    network_names_by_chain_id = (
        config_defaults.get_default_network_names_by_chain_id()
    )
    block_explorers = config_defaults.get_default_block_explorers()
    assert set(network_names_by_chain_id.values()) == set(
        block_explorers.keys()
    )
