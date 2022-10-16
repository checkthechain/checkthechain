import pytest

import ctc


function_tests = [
    (
        ctc.async_normalize_erc4626_assets,
        {
            'token': '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            'assets': 36046586261330396137,
            'block': 15758437,
        },
        36.046586261330396137,
    ),
    (
        ctc.async_normalize_erc4626_assets,
        {
            'token': '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            'assets': [36046586261330396137, 3604658626133039613, 360465862613303961],
            'block': 15758437,
        },
        [36.046586261330396137, 3.604658626133039613, .360465862613303961],
    ),
    (
        ctc.async_normalize_erc4626_shares,
        {
            'token': '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            'shares': 33057396587641309018,
            'block': 15758437,
        },
        33.057396587641309018,
    ),
    (
        ctc.async_normalize_erc4626_shares,
        {
            'token': '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            'shares': [33057396587641309018, 3305739658764130901, 330573965876413090],
            'block': 15758437,
        },
        [33.057396587641309018, 3.3057396587641309018, .33057396587641309018],
    ),
    (
        ctc.async_normalize_erc4626s_assets,
        {
            'tokens': [
                '0xac3e018457b222d93114458476f3e3416abbe38f',
                '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
                '0x63bbb71b68c76b78243d0a4aa463d34536788a15',
            ],
            'assets': [33057396587641309018, 33057396587641309018, 33057396587641309018],
            'block': 15758437,
        },
        [33.057396587641309018, 33.057396587641309018, 33057396587641.309018],
    ),
    (
        ctc.async_normalize_erc4626s_shares,
        {
            'tokens': [
                '0xac3e018457b222d93114458476f3e3416abbe38f',
                '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
                '0x63bbb71b68c76b78243d0a4aa463d34536788a15',
            ],
            'shares': [33057396587641309018, 33057396587641309018, 33057396587641309018],
            'block': 15758437,
        },
        [33.057396587641309018, 33.057396587641309018, 33057396587641.309018],
    ),
]


@pytest.mark.parametrize('call', function_tests)
async def test_erc4626_normalize_functions(call):
    f, kwargs, target = call
    actual = await f(**kwargs)
    assert target == actual
