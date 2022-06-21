from __future__ import annotations

import typing

from ctc import db
from ctc import spec

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


network_payload_locations = {
    'mainnet': ['ethereum-addresses', 'Ethereum Mainnet'],
    'kovan': ['ethereum-addresses', 'Kovan Testnet'],
    'rinkeby': ['ethereum-addresses', 'Rinkeby Testnet'],
    'bnb': ['bnb-chain-addresses-price', 'BNB Chain Mainnet'],
    'bnb_testnet': ['bnb-chain-addresses-price', 'BNB Chain Testnet'],
    'polygon': ['matic-addresses', 'Polygon Mainnet'],
    'polygon_testnet': ['matic-addresses', 'Polygon Mainnet'],
    'gnosis': ['data-feeds-gnosis-chain', 'Gnosis Chain Mainnet'],
    'heco': ['huobi-eco-chain-price-feeds', 'HECO Mainnet'],
    'avalanche': ['avalanche-price-feeds', 'Avalanche Mainnet'],
    'avalanche_testnet': ['avalanche-price-feeds', 'Avalanche Testnet'],
    'fantom': ['fantom-price-feeds', 'Fantom Mainnet'],
    'arbitrum': ['arbitrum-price-feeds', 'Arbitrum Mainnet'],
    'arbitrum_rinkeby': ['arbitrum-price-feeds', 'Arbitrum Rinkeby'],
    'harmony': ['harmony-price-feeds', 'Harmony Mainnet'],
    'harmony_testnet': ['harmony-price-feeds', 'Harmony Testnet'],
    # 'solana': ['data-feeds-solana', 'Solana Mainnet'],
    # 'solana_testnet': ['data-feeds-solana', 'Solana Devnet'],
    'optimism': ['optimism-price-feeds', 'Optimism Mainnet'],
    'optimism_kovan': ['optimism-price-feeds', 'Optimism Kovan'],
    'moonriver': ['data-feeds-moonriver', 'Moonriver Mainnet'],
    'moonbeam': ['data-feeds-moonbeam', 'Moonbeam Mainnet'],
}


async def async_get_complete_feed_payload() -> ChainlinkFeedPayload:

    import aiohttp

    url = 'https://cl-docs-addresses.web.app/addresses.json'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def async_get_network_feed_data(
    network: spec.NetworkName,
    payload: ChainlinkFeedPayload | None = None,
) -> typing.Sequence[ChainlinkProxyData]:
    if payload is None:
        payload = await async_get_complete_feed_payload()

    if network in network_payload_locations:
        network_group, network_name = network_payload_locations[network]
    else:
        raise Exception('unknown network')

    for network_data in payload[network_group]['networks']:
        if network_data['name'] == network_name:
            return network_data['proxies']
    else:
        raise Exception('could not find network feeds')


async def async_import_network_to_db(
    network: ChainlinkNetworkName,
    payload: ChainlinkFeedPayload | None = None,
    engine: toolsql.SAEngine | None = None,
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

    if engine is None:
        engine = db.create_engine(schema_name='chainlink', network=network)

    if engine is None:
        raise Exception('cannot find db table to import to')

    with engine.begin() as conn:

        await chainlink_statements.async_upsert_feeds(
            feeds=feeds,
            network=network,
            conn=conn,
        )


def summarize_payload(payload: ChainlinkFeedPayload) -> None:
    for group in payload.keys():
        print(group)
        for network in payload[group]['networks']:
            print(
                '    -',
                network['name'],
                '(' + str(len(network['proxies'])) + ')',
            )
