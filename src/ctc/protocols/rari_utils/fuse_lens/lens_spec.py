from __future__ import annotations

import typing
from typing_extensions import TypedDict

from ctc import rpc
from ctc import spec


def get_lens_address(
    lens_name: str,
    network: spec.NetworkReference | None = None,
    *,
    provider: spec.ProviderReference = None,
) -> spec.Address:

    if network is None:
        provider = rpc.get_provider(provider)
        network = provider['network']
        if network is None:
            raise Exception('could not determine network')

    if network == 'mainnet':

        if lens_name == 'primary':
            return '0x6dc585ad66a10214ef0502492b0cc02f0e836eec'
        elif lens_name == 'secondary':
            return '0xc76190e04012f26a364228cfc41690429c44165d'
        else:
            raise Exception('unknown lens name: ' + str(lens_name))

    elif network == 'arbitrum':

        if lens_name == 'primary':
            return '0xd6e194af3d9674b62d1b30ec676030c23961275e'
        elif lens_name == 'secondary':
            return '0x32ca4e5d75ecb06f33846055652c831f6e7a6924'
        else:
            raise Exception('unknown lens name: ' + str(lens_name))

    else:
        raise Exception('no lens for network: ' + str(network))


class FusePool(TypedDict):
    name: str
    creator: spec.Address
    comptroller: spec.Address
    block_posted: int
    timestamp_posted: int


class FusePoolData(TypedDict):
    total_supply: int
    total_borrow: int
    underlying_tokens: typing.Sequence[spec.Address]
    underlying_symbols: typing.Sequence[str]
    whitelisted_admin: bool


class FusePoolAsset(TypedDict):
    ftoken: spec.Address
    underlying_token: spec.Address
    underlying_name: str
    underlying_symbol: str
    underlying_decimals: int
    underlying_balance: int
    supply_rate_per_block: int
    borrow_rate_per_block: int
    total_supply: int
    total_borrow: int
    supply_balance: int
    borrow_balance: int
    liquidity: int
    membership: bool
    exchange_rate: int
    underlying_price: int
    oracle: spec.Address
    collateral_factor: int
    reserve_factor: int
    admin_fee: int
    fuse_fee: int
    borrow_guardian_paused: bool


class FusePoolUser(TypedDict):
    account: spec.Address
    total_borrow: int
    total_collateral: int
    health: int
    assets: typing.Sequence[FusePoolAsset]


class CTokenOwnership(TypedDict):
    ctoken: spec.Address
    admin: spec.Address
    admin_has_rights: bool
    fuse_admin_has_rights: bool


class PublicPoolsWithData(TypedDict):
    public_pools: typing.Sequence[FusePool]
    data: typing.Sequence['ReturnPoolSummary']
    errored: typing.Sequence[bool]


class ReturnPoolSummary(TypedDict):
    total_supply: int
    total_borrow: int
    underlying_tokens: typing.Sequence[spec.Address]
    underlying_symbols: typing.Sequence[str]
    whitelisted_admin: bool


class ReturnPoolUsersWithData(TypedDict):
    users: typing.Sequence[FusePoolUser]
    close_factor: int
    liquidation_incentive: int


class ReturnPoolsUsersWithData(TypedDict):
    users: typing.Sequence[typing.Sequence[FusePoolUser]]
    close_factors: typing.Sequence[int]
    liquidation_incentives: typing.Sequence[int]
    errored: typing.Sequence[bool]


class ReturnPublicPoolUsersWithData(TypedDict):
    comptrollers: typing.Sequence[spec.Address]
    users: typing.Sequence[FusePoolUser]
    close_factors: typing.Sequence[int]
    liquidation_incentives: typing.Sequence[int]
    errored: typing.Sequence[bool]


class ReturnPoolsBySupplier(TypedDict):
    indices: typing.Sequence[spec.Address]
    account_pools: typing.Sequence[FusePool]


class ReturnPoolsBySupplierWithData(TypedDict):
    indices: typing.Sequence[spec.Address]
    account_pools: typing.Sequence[FusePool]
    data: typing.Sequence[FusePoolData]
    errored: typing.Sequence[bool]


class UserSummary(TypedDict):
    supply_balance: int
    borrow_balance: int
    error: bool


class PoolUserSummary(TypedDict):
    supply_balance: int
    borrow_balance: int


class ReturnWhitelistedPoolsByAccountWithData(TypedDict):
    indices: typing.Sequence[int]
    account_pools: typing.Sequence[FusePool]
    data: typing.Sequence[FusePoolData]
    errored: typing.Sequence[bool]


def fuse_pool_to_dict(as_list: typing.Sequence[typing.Any]) -> FusePool:

    keys = list(FusePool.__annotations__.keys())
    if len(as_list) != len(keys):
        raise Exception('invalid number of items')

    return {
        'name': as_list[0],
        'creator': as_list[1],
        'comptroller': as_list[2],
        'block_posted': as_list[3],
        'timestamp_posted': as_list[4],
    }


def fuse_pool_data_to_dict(
    as_list: typing.Sequence[typing.Any],
) -> FusePoolData:

    keys = list(FusePoolData.__annotations__.keys())
    if len(as_list) != len(keys):
        raise Exception('invalid number of items')

    return {
        'total_supply': as_list[0],
        'total_borrow': as_list[1],
        'underlying_tokens': as_list[2],
        'underlying_symbols': as_list[3],
        'whitelisted_admin': as_list[4],
    }


def fuse_pool_asset_to_dict(
    as_list: typing.Sequence[typing.Any],
) -> FusePoolAsset:

    keys = list(FusePoolAsset.__annotations__.keys())
    if len(as_list) != len(keys):
        raise Exception('invalid number of items')

    return {
        'ftoken': as_list[0],
        'underlying_token': as_list[1],
        'underlying_name': as_list[2],
        'underlying_symbol': as_list[3],
        'underlying_decimals': as_list[4],
        'underlying_balance': as_list[5],
        'supply_rate_per_block': as_list[6],
        'borrow_rate_per_block': as_list[7],
        'total_supply': as_list[8],
        'total_borrow': as_list[9],
        'supply_balance': as_list[10],
        'borrow_balance': as_list[11],
        'liquidity': as_list[12],
        'membership': as_list[13],
        'exchange_rate': as_list[14],
        'underlying_price': as_list[15],
        'oracle': as_list[16],
        'collateral_factor': as_list[17],
        'reserve_factor': as_list[18],
        'admin_fee': as_list[19],
        'fuse_fee': as_list[20],
        'borrow_guardian_paused': as_list[21],
    }


def fuse_pool_user_to_dict(
    as_list: typing.Sequence[typing.Any],
) -> FusePoolUser:

    keys = list(FusePoolUser.__annotations__.keys())
    if len(as_list) != len(keys):
        raise Exception('invalid number of items')

    result: FusePoolUser = {
        'account': as_list[0],
        'total_borrow': as_list[1],
        'total_collateral': as_list[2],
        'health': as_list[3],
        'assets': as_list[4],
    }

    result['assets'] = [
        fuse_pool_asset_to_dict(asset)
        for asset in typing.cast(typing.List[typing.Any], result['assets'])
    ]
    return result


def return_pool_summary_to_dict(
    as_list: typing.Sequence[typing.Any],
) -> ReturnPoolSummary:

    keys = list(ReturnPoolSummary.__annotations__.keys())
    if len(as_list) != len(keys):
        raise Exception('invalid number of items')

    return {
        'total_supply': as_list[0],
        'total_borrow': as_list[1],
        'underlying_tokens': as_list[2],
        'underlying_symbols': as_list[3],
        'whitelisted_admin': as_list[4],
    }


def return_pool_users_with_data_to_dict(
    as_list: typing.Sequence[typing.Any],
) -> ReturnPoolUsersWithData:
    keys = list(ReturnPoolUsersWithData.__annotations__.keys())
    if len(as_list) != len(keys):
        raise Exception('invalid number of items')

    result: ReturnPoolUsersWithData = {
        'users': as_list[0],
        'close_factor': as_list[1],
        'liquidation_incentive': as_list[2],
    }

    result['users'] = [
        fuse_pool_user_to_dict(user)
        for user in typing.cast(typing.List[typing.Any], result['users'])
    ]

    return result
