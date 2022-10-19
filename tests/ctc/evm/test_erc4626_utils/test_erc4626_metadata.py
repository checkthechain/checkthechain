from __future__ import annotations

import ctc


async def test_get_erc4626_asset():
    token = '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a'
    result = await ctc.async_get_erc4626_asset(token=token)
    assert result == '0xae7ab96520de3a18e5e111b5eaab095312d7fe84'


async def test_get_erc4626_assets():
    tokens = [
        '0xac3e018457b222d93114458476f3e3416abbe38f',
        '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
        '0x63bbb71b68c76b78243d0a4aa463d34536788a15',
        '0xa953f0c594365b821a847e7b9f4722e338526699',
        '0x91ee5184763d0b80f8dfdcbde762b5d13ad295f4',
        '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
    ]
    assets = [
        '0x5e8422345238f34275888049021821e8e08caa1f',
        '0xae7ab96520de3a18e5e111b5eaab095312d7fe84',
        '0x24eb7f255a9fe448940234bf74d95c8925ebd753',
        '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
        '0x06325440d014e39736583c165c2963ba99faf14e',
        '0x6b3595068778dd592e39a122f4f5a5cf09c90fe2',
    ]

    results = await ctc.async_get_erc4626s_assets(tokens)
    assert results == assets
