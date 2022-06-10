# """
# ## Resources
# for overview of different chains see
# - https://github.com/ethereum-lists/chains
# - https://chainlist.org/
# """

# from __future__ import annotations

# import os

# from ctc import config
# from ctc import spec
# from ctc.toolbox import search_utils
# from ctc.toolbox import store_utils


# def get_network_name(network: spec.NetworkReference) -> spec.NetworkName:

#     if isinstance(network, str):
#         return network

#     network_names_by_id = {
#         1: 'mainnet',
#         3: 'ropsten',
#         4: 'rinkeby',
#         5: 'goerli',
#         42: 'kovan',
#         137: 'polygon',
#         57: 'bsc',
#         100: 'xdai',
#         43114: 'avax',
#         250: 'fantom',
#         42161: 'arbitrum',
#         10: 'optimism',
#     }
#     if network in network_names_by_id:
#         return network_names_by_id[network]

#     # return get_network_metadata(network=network)['name']


# def get_network_chain_id(network: spec.NetworkReference) -> spec.NetworkId:

#     if isinstance(network, int):
#         return network

#     network_ids_by_name = {
#         'mainnet': 1,
#         'ropsten': 3,
#         'rinkeby': 4,
#         'goerli': 5,
#         'kovan': 42,
#         'polygon': 137,
#         'bsc': 56,
#         'xdai': 100,
#         'avax': 43114,
#         'fantom': 250,
#         'arbitrum': 42161,
#         'optimism': 10,
#     }

#     if network in network_ids_by_name:
#         return network_ids_by_name[network]

#     # return get_network_metadata(network=network)['chain_id']


# def get_network_metadata(
#     network: spec.NetworkReference,
# ) -> spec.NetworkMetadata:

#     default_network_data = load_networks_from_disk()
#     config_network_data = config.get_networks()
#     all_network_data = dict(default_network_data, **config_network_data)
#     network_list = list(all_network_data.values())

#     if network is None:
#         network = config.get_default_network()

#     if isinstance(network, int):
#         return search_utils.get_matching_entry(
#             sequence=network_list,
#             query={'chain_id': network},
#         )

#     elif isinstance(network, str):
#         return search_utils.get_matching_entry(
#             sequence=network_list,
#             query={'name': network},
#         )

#     else:
#         raise Exception('unknown network format: ' + str(network))


# def get_networks() -> dict[spec.NetworkName, spec.NetworkMetadata]:
#     # use filesystem backend for now
#     return load_networks_from_disk()


##
## # filesystem backend
##


#def load_networks_from_disk(
#    use_default: bool = False,
#) -> dict[spec.NetworkName, spec.NetworkMetadata]:
#    path = get_networks_file_path(use_default=use_default)
#    raw_data = store_utils.load_file_data(path)
#    return {network['name']: network for network in raw_data}


#def get_networks_file_path(use_default: bool = False) -> str:
#    if use_default:
#        data_root = config.get_default_data_dir()
#    else:
#        data_root = config.get_data_dir()
#    return os.path.join(data_root, 'networks.csv')
