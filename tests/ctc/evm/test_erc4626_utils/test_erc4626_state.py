import pytest

import ctc


examples = [
    #
    # conversions
    (
        ctc.async_convert_to_erc4626_assets,
        {
            'token': '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            'shares': 33057396587641309018,
            'block': 15758437,
        },
        36046586261330396116,
    ),
    (
        ctc.async_convert_to_erc4626_assets_by_block,
        {
            'token': '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            'shares': 36046586261330396116,
            'blocks': [15753437, 15755437, 15758437],
        },
        [39300705063586544508, 39306071113334582763, 39306071113334582763],
    ),
    (
        ctc.async_convert_to_erc4626_shares,
        {
            'token': '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            'assets': 36046586261330396116,
            'block': 15758437,
        },
        33057396587641309017,
    ),
    (
        ctc.async_convert_to_erc4626_shares_by_block,
        {
            'token': '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            'assets': 36046586261330396116,
            'blocks': [15753437, 15755437, 15758437],
        },
        [33061910186935339726, 33057396587641309017, 33057396587641309017],
    ),
    (
        ctc.async_convert_to_erc4626s_assets,
        {
            'tokens': [
                '0xac3e018457b222d93114458476f3e3416abbe38f',
                '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
                '0x63bbb71b68c76b78243d0a4aa463d34536788a15',
            ],
            'shares': [
                36046586261330396116,
                36046586261330396116,
                36046586261330396116,
            ],
            'block': 15758437,
        },
        [36046879858304264774, 39306071113334582763, 22540386606747723164],
    ),
    (
        ctc.async_convert_to_erc4626s_shares,
        {
            'tokens': [
                '0xac3e018457b222d93114458476f3e3416abbe38f',
                '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
                '0x63bbb71b68c76b78243d0a4aa463d34536788a15',
            ],
            'assets': [
                36046586261330396116,
                36046586261330396116,
                36046586261330396116,
            ],
            'block': 15758437,
        },
        [36046292666747835204, 33057396587641309017, 57645700748830813489],
    ),
    #
    # maxes
    (
        ctc.async_get_erc4626_max_deposit,
        {
            'token': '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
            'receiver': '0xbb443d6740322293fcee4414d03978c7e4bf5d55',
            'block': 15695459,
        },
        4803576.925987547,
    ),
    (
        ctc.async_get_erc4626_max_deposit_by_block,
        {
            'token': '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
            'receiver': '0xbb443d6740322293fcee4414d03978c7e4bf5d55',
            'blocks': [15669739, 15670658, 15695459],
        },
        [4804057.891971781, 4804056.391971781, 4803576.925987547],
    ),
    (
        ctc.async_get_erc4626_max_mint,
        {
            'token': '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
            'receiver': '0xbb443d6740322293fcee4414d03978c7e4bf5d55',
            'block': 15669739,
        },
        4.361514e-12,
    ),
    (
        ctc.async_get_erc4626_max_mint_by_block,
        {
            'token': '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
            'receiver': '0xbb443d6740322293fcee4414d03978c7e4bf5d55',
            'blocks': [15669739, 15670658, 15695459],
        },
        [4.361514e-12, 4.361512e-12, 4.361077e-12],
    ),
    (
        ctc.async_get_erc4626_max_redeem,
        {
            'token': '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
            'owner': '0x4a66d86fc7cc600cda4ad90c176d13b45e5c539c',
            'block': 15709739,
        },
        1.45,
    ),
    (
        ctc.async_get_erc4626_max_redeem_by_block,
        {
            'token': '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
            'owner': '0x4a66d86fc7cc600cda4ad90c176d13b45e5c539c',
            'blocks': [15669739, 15670658, 15695459],
        },
        [10.0, 1.5, 1.45],
    ),
    (
        ctc.async_get_erc4626_max_withdraw,
        {
            'token': '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
            'owner': '0x4a66d86fc7cc600cda4ad90c176d13b45e5c539c',
            'block': 15709739,
        },
        1.45,
    ),
    (
        ctc.async_get_erc4626_max_withdraw_by_block,
        {
            'token': '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
            'owner': '0x4a66d86fc7cc600cda4ad90c176d13b45e5c539c',
            'blocks': [15669739, 15670658, 15695459],
        },
        [10.0, 1.5, 1.45],
    ),
    (
        ctc.async_get_erc4626_total_assets,
        {
            'token': '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
            'block': 15709739,
        },
        12.45,
    ),
    (
        ctc.async_get_erc4626_total_assets_by_block,
        {
            'token': '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
            'blocks': [15669739, 15670658, 15695459],
        },
        [10.0, 11.5, 12.45],
    ),
    (
        ctc.async_get_erc4626s_max_deposits,
        {
            'tokens': [
                '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
                '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            ],
            'receiver': '0xbb443d6740322293fcee4414d03978c7e4bf5d55',
            'block': 15695459,
        },
        [4803576.925987547, 1.157920892373162e+59],
    ),
    (
        ctc.async_get_erc4626s_max_mints,
        {
            'tokens': [
                '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
                '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            ],
            'receiver': '0xbb443d6740322293fcee4414d03978c7e4bf5d55',
            'block': 15695459,
        },
        [4.361077e-12, 1.157920892373162e+59],
    ),
    (
        ctc.async_get_erc4626s_max_redeems,
        {
            'tokens': [
                '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
                '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            ],
            'owner': '0xbb443d6740322293fcee4414d03978c7e4bf5d55',
            'block': 15695459,
        },
        [0.0, 26.91118640140283],
    ),
    (
        ctc.async_get_erc4626s_max_withdraws,
        {
            'tokens': [
                '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
                '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            ],
            'owner': '0xbb443d6740322293fcee4414d03978c7e4bf5d55',
            'block': 15695459,
        },
        [0, 29.306685853423535272],
    ),
    (
        ctc.async_get_erc4626s_total_assets,
        {
            'tokens': [
                '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
                '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            ],
            'block': 15695459,
        },
        [12.45, 29.328946660367173],
    ),
    (
        ctc.async_preview_erc4626_deposit,
        {
            'token': '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            'assets': 32000000,
            'block': 15725459,
        },
        29363518,
    ),
    (
        ctc.async_preview_erc4626_deposit_by_block,
        {
            'token': '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            'assets': 32000000,
            'blocks': [15669739, 15670658, 15695459],
        },
        [29397349, 29397349, 29384351]
    ),
    (
        ctc.async_preview_erc4626_mint,
        {
            'token': '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            'shares': 32000000,
            'block': 15725459,
        },
        34873206,
    ),
    (
        ctc.async_preview_erc4626_mint_by_block,
        {
            'token': '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            'shares': 32000000,
            'blocks': [15669739, 15670658, 15695459],
        },
        [34833072, 34833072, 34848481],
    ),
    (
        ctc.async_preview_erc4626_redeem,
        {
            'token': '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            'shares': 32000000,
            'block': 15725459,
        },
        34873205,
    ),
    (
        ctc.async_preview_erc4626_redeem_by_block,
        {
            'token': '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            'shares': 32000000,
            'blocks': [15669739, 15670658, 15695459],
        },
        [34833071, 34833071, 34848480],
    ),
    (
        ctc.async_preview_erc4626_withdraw,
        {
            'token': '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            'assets': 32000000,
            'block': 15725459,
        },
        29363519,
    ),
    (
        ctc.async_preview_erc4626_withdraw_by_block,
        {
            'token': '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            'assets': 32000000,
            'blocks': [15669739, 15670658, 15695459],
        },
        [29397350, 29397350, 29384352],
    ),
    (
        ctc.async_preview_erc4626s_deposits,
        {
            'tokens': [
                '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
                '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            ],
            'assets': 32000000,
            'block': 15725459,
        },
        [32000000, 29363518]
    ),
    (
        ctc.async_preview_erc4626s_mints,
        {
            'tokens': [
                '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
                '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            ],
            'shares': 32000000,
            'block': 15725459,
        },
        [32000000, 34873206],
    ),
    (
        ctc.async_preview_erc4626s_redeems,
        {
            'tokens': [
                '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
                '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            ],
            'shares': 32000000,
            'block': 15725459,
        },
        [31999999, 34873205],
    ),
    (
        ctc.async_preview_erc4626s_withdraws,
        {
            'tokens': [
                '0xa384c9cca28cc7a58093e4e9a0acacf8c20072fd',
                '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            ],
            'assets': 32000000,
            'block': 15725459,
        },
        [32000001, 29363519],
    ),
]


@pytest.mark.parametrize('call', examples)
async def test_erc4626_state_functions(call):
    f, kwargs, target = call
    actual = await f(**kwargs)
    assert target == actual
