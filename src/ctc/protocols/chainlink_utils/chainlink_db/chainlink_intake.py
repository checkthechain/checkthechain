from __future__ import annotations

import typing

import toolsql

from ctc import config
from ctc import evm
from ctc import spec
from ctc import db

from . import chainlink_schema_defs
from . import chainlink_statements


if typing.TYPE_CHECKING:

    import toolsql

    RawChainlinkFeed = typing.Mapping[typing.Any, typing.Any]

    ChainlinkFeedPayload = typing.Mapping[
        'ChainlinkNetworkName',
        'ChainlinkNetworkGroup',
    ]
    ChainlinkNetworkName = str

    class ChainlinkNetworkGroup(typing.TypedDict):
        title: str
        feedType: str
        networks: list['ChainlinkNetworkData']

    class ChainlinkNetworkData(typing.TypedDict):
        name: str
        url: str
        networkType: str
        proxies: list[ChainlinkProxyData]

    class ChainlinkProxyData(typing.TypedDict):
        pair: str
        assetName: str
        deviationThreshold: int
        heartbeat: str
        decimals: int
        proxy: str
        feedCategory: str
        feedType: str


# # legacy version of chainlink payload data
# _legacy_network_payload_locations: typing.Mapping[spec.NetworkName, tuple[str, str]] = {
#     'ethereum': ('ethereum-addresses', 'Ethereum Mainnet'),
#     'kovan': ('ethereum-addresses', 'Kovan Testnet'),
#     'rinkeby': ('ethereum-addresses', 'Rinkeby Testnet'),
#     'bnb': ('bnb-chain-addresses-price', 'BNB Chain Mainnet'),
#     'bnb_testnet': ('bnb-chain-addresses-price', 'BNB Chain Testnet'),
#     'polygon': ('matic-addresses', 'Polygon Mainnet'),
#     'polygon_mumbai': ('matic-addresses', 'Mumbai Testnet'),
#     'gnosis': ('data-feeds-gnosis-chain', 'Gnosis Chain Mainnet'),
#     'heco': ('huobi-eco-chain-price-feeds', 'HECO Mainnet'),
#     'avalanche': ('avalanche-price-feeds', 'Avalanche Mainnet'),
#     'avalanche_fuji': ('avalanche-price-feeds', 'Avalanche Testnet'),
#     'fantom': ('fantom-price-feeds', 'Fantom Mainnet'),
#     'arbitrum': ('arbitrum-price-feeds', 'Arbitrum Mainnet'),
#     'arbitrum_rinkeby': ('arbitrum-price-feeds', 'Arbitrum Rinkeby'),
#     'harmony': ('harmony-price-feeds', 'Harmony Mainnet'),
#     'harmony_testnet': ('harmony-price-feeds', 'Harmony Testnet'),
#     # 'solana': ('data-feeds-solana', 'Solana Mainnet'),
#     # 'solana_testnet': ('data-feeds-solana', 'Solana Devnet'),
#     'optimism': ('optimism-price-feeds', 'Optimism Mainnet'),
#     'optimism_kovan': ('optimism-price-feeds', 'Optimism Kovan'),
#     'moonriver': ('data-feeds-moonriver', 'Moonriver Mainnet'),
#     'moonbeam': ('data-feeds-moonbeam', 'Moonbeam Mainnet'),
# }

network_payload_locations: typing.Mapping[spec.NetworkName, tuple[str, int]] = {
    'ethereum': ('ethereum', 0),
    'goerli': ('ethereum', 1),
    'bnb': ('bnb-chain', 0),
    'bnb_testnet': ('bnb-chain', 1),
    'polygon': ('polygon', 0),
    'polygon_mumbai': ('polygon', 0),
    'gnosis': ('gnosis-chain', 0),
    'heco': ('heco-chain', 0),
    'avalanche': ('avalanche', 0),
    'avalanche_fuji': ('avalanche', 1),
    'fantom': ('fantom', 0),
    'fantom_testnet': ('fantom', 1),
    'arbitrum': ('arbitrum', 0),
    'arbitrum_rinkeby': ('arbitrum', 1),
    'harmony': ('harmony', 0),
    'optimism': ('optimism', 0),
    'optimism_goerli': ('optimism', 1),
    'moonriver': ('moonriver', 0),
    'moonbeam': ('moonbeam', 0),
    'metis': ('metis', 0),
    'klaytn': ('klaytn', 0),
}


async def async_get_complete_feed_payload() -> ChainlinkFeedPayload:

    import aiohttp

    url = 'https://cl-docs-addresses.web.app/addresses.json'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()  # type: ignore


async def async_get_network_feed_data(
    network: spec.NetworkReference,
    payload: ChainlinkFeedPayload | None = None,
) -> typing.Sequence[ChainlinkProxyData]:
    if payload is None:
        payload = await async_get_complete_feed_payload()

    if network in network_payload_locations:
        if isinstance(network, int):
            network = evm.get_network_chain_id(network)
        if not isinstance(network, str):
            raise Exception('unknown network type: ' + str(type(network)))
        network_group, index = network_payload_locations[network]
    else:
        raise Exception('unknown network')

    return payload[network_group]['networks'][index]['proxies']


async def async_import_networks_to_db(
    networks: typing.Sequence[ChainlinkNetworkName] | None = None,
    *,
    db_config: toolsql.DBConfig,
    payload: ChainlinkFeedPayload | None = None,
    verbose: bool = True,
) -> None:
    """import multiple networks of feeds to db

    by default import all networks
    """

    if payload is None:
        payload = await async_get_complete_feed_payload()

    # determine which networks to use
    if networks is None:

        known_networks = {
            datum['name'] for datum in evm.get_networks().values()
        }

        networks = []
        for network_name in network_payload_locations.keys():
            network_group, index = network_payload_locations[network_name]
            if (
                network_name in known_networks
                and network_group in payload
                and len(payload[network_group]['networks']) > index
            ):
                networks.append(network_name)

    #         # use all networks
    #         locations_to_network = {
    #             v: k for k, v in network_payload_locations.items()
    #         }
    #         networks = []
    #         for key in payload.keys():
    #             for network_data in payload[key]['networks']:
    #                 subkey = network_data['name']
    #                 if (key, subkey) in locations_to_network:
    #                     network = locations_to_network[(key, subkey)]
    #                     networks.append(network)

    if verbose:
        import toolstr
        from ctc import cli

        styles = cli.get_cli_styles()

        toolstr.print(
            'Adding Chainlink feed metadata to db for',
            toolstr.add_style(
                str(len(networks)), styles['description'] + ' bold'
            ),
            'networks...',
        )

    # add each network
    for network in networks:

        # create table
        table_schema = db.get_table_schema(
            'chainlink_feeds', context={'network': network}
        )
        with toolsql.connect(db_config) as conn:
            toolsql.create_table(
                table_schema,
                if_not_exists=True,
                conn=conn,
                confirm=True,
            )

        # insert feed rows
        async with toolsql.async_connect(db_config) as conn:
            await async_import_network_to_db(
                network=network,
                payload=payload,
                conn=conn,
                verbose=verbose,
                indent=4,
            )


async def async_import_network_to_db(
    network: ChainlinkNetworkName,
    *,
    payload: ChainlinkFeedPayload | None = None,
    conn: toolsql.AsyncConnection,
    verbose: bool = True,
    indent: int | str | None = None,
) -> None:

    raw_feeds = await async_get_network_feed_data(
        network=network, payload=payload
    )

    rename_fields = {
        'proxy': 'address',
        'pair': 'name',
        'deviationThreshold': 'deviation',
        'heartbeat': 'heartbeat',
        'decimals': 'decimals',
        'assetName': 'asset',
        'feedType': 'asset_type',
        'feedCategory': 'status',
    }

    feeds: typing.Sequence[typing.Mapping[str, typing.Any]] = [
        {key: raw_feed[raw_key] for raw_key, key in rename_fields.items()}  # type: ignore
        for raw_feed in raw_feeds
    ]

    await chainlink_statements.async_upsert_feeds(
        feeds=feeds,
        context=dict(network=network),
        conn=conn,
    )

    if verbose:
        import toolstr
        from ctc import cli

        if indent is None:
            indent = ''
        if isinstance(indent, int):
            indent = ' ' * indent

        styles = cli.get_cli_styles()

        toolstr.print(
            indent + 'added',
            toolstr.add_style(str(len(feeds)), styles['description'] + ' bold'),
            toolstr.add_style(network, styles['metavar']),
            'Chainlink feeds to db',
        )


def print_payload_summary(payload: ChainlinkFeedPayload) -> None:
    for group in payload.keys():
        print(group)
        for network in payload[group]['networks']:
            print(
                '    -',
                network['name'],
                '(' + str(len(network['proxies'])) + ')',
            )


async def async_intake_aggregator_update(
    *,
    feed: spec.Address,
    aggregator: spec.Address,
    block_number: int,
    context: spec.Context,
) -> None:

    db_config = config.get_context_db_config(
        schema_name='chainlink',
        context=context,
    )
    async with toolsql.async_connect(db_config) as conn:
        await chainlink_statements.async_upsert_aggregator_update(
            feed=feed,
            aggregator=aggregator,
            block_number=block_number,
            context=context,
            conn=conn,
        )


async def async_intake_aggregator_updates(
    updates: typing.Sequence[chainlink_schema_defs._FeedAggregatorUpdate],
    context: spec.Context,
) -> None:

    db_config = config.get_context_db_config(
        schema_name='chainlink',
        context=context,
    )
    async with toolsql.async_connect(db_config) as conn:
        await chainlink_statements.async_upsert_aggregator_updates(
            updates=updates,
            conn=conn,
            context=context,
        )

