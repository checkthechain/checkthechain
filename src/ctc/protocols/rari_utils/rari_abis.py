from ctc import spec


contract_examples: dict[str, spec.Address] = {
    'PoolDirectory': '0x835482fe0532f169024d5e9410199369aad5c77e',
    'Token': '0xfd3300a9a74b3250f1b2abc12b47611171910b07',
    'Comptroller': '0xc54172e34046c1653d1920d40333dd358c7a1af4',
    'InterestRateModel': '0x075538650a9c69ac8019507a7dd1bd879b12c1d7',
    'Oracle': '0x4d10bc156fbad2474a94f792fe0d6c3261469cdd',
}


pool_directory_abis = {
    'AdminChanged': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'previousAdmin',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'newAdmin',
                'type': 'address',
            },
        ],
        'name': 'AdminChanged',
        'type': 'event',
    },
    'Upgraded': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'implementation',
                'type': 'address',
            }
        ],
        'name': 'Upgraded',
        'type': 'event',
    },
    'admin': {
        'inputs': [],
        'name': 'admin',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'changeAdmin': {
        'inputs': [
            {'internalType': 'address', 'name': 'newAdmin', 'type': 'address'}
        ],
        'name': 'changeAdmin',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'implementation': {
        'inputs': [],
        'name': 'implementation',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'upgradeTo': {
        'inputs': [
            {
                'internalType': 'address',
                'name': 'newImplementation',
                'type': 'address',
            }
        ],
        'name': 'upgradeTo',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'upgradeToAndCall': {
        'inputs': [
            {
                'internalType': 'address',
                'name': 'newImplementation',
                'type': 'address',
            },
            {'internalType': 'bytes', 'name': 'data', 'type': 'bytes'},
        ],
        'name': 'upgradeToAndCall',
        'outputs': [],
        'stateMutability': 'payable',
        'type': 'function',
    },
    'AdminWhitelistUpdated': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'address[]',
                'name': 'admins',
                'type': 'address[]',
            },
            {
                'indexed': False,
                'internalType': 'bool',
                'name': 'status',
                'type': 'bool',
            },
        ],
        'name': 'AdminWhitelistUpdated',
        'type': 'event',
    },
    'OwnershipTransferred': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'previousOwner',
                'type': 'address',
            },
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'newOwner',
                'type': 'address',
            },
        ],
        'name': 'OwnershipTransferred',
        'type': 'event',
    },
    'PoolRegistered': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'index',
                'type': 'uint256',
            },
            {
                'components': [
                    {
                        'internalType': 'string',
                        'name': 'name',
                        'type': 'string',
                    },
                    {
                        'internalType': 'address',
                        'name': 'creator',
                        'type': 'address',
                    },
                    {
                        'internalType': 'address',
                        'name': 'comptroller',
                        'type': 'address',
                    },
                    {
                        'internalType': 'uint256',
                        'name': 'blockPosted',
                        'type': 'uint256',
                    },
                    {
                        'internalType': 'uint256',
                        'name': 'timestampPosted',
                        'type': 'uint256',
                    },
                ],
                'indexed': False,
                'internalType': 'struct FusePoolDirectory.FusePool',
                'name': 'pool',
                'type': 'tuple',
            },
        ],
        'name': 'PoolRegistered',
        'type': 'event',
    },
    '_editAdminWhitelist': {
        'inputs': [
            {
                'internalType': 'address[]',
                'name': 'admins',
                'type': 'address[]',
            },
            {'internalType': 'bool', 'name': 'status', 'type': 'bool'},
        ],
        'name': '_editAdminWhitelist',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_editDeployerWhitelist': {
        'inputs': [
            {
                'internalType': 'address[]',
                'name': 'deployers',
                'type': 'address[]',
            },
            {'internalType': 'bool', 'name': 'status', 'type': 'bool'},
        ],
        'name': '_editDeployerWhitelist',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setDeployerWhitelistEnforcement': {
        'inputs': [{'internalType': 'bool', 'name': 'enforce', 'type': 'bool'}],
        'name': '_setDeployerWhitelistEnforcement',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'adminWhitelist': {
        'inputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'name': 'adminWhitelist',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'bookmarkPool': {
        'inputs': [
            {
                'internalType': 'address',
                'name': 'comptroller',
                'type': 'address',
            }
        ],
        'name': 'bookmarkPool',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'deployPool': {
        'inputs': [
            {'internalType': 'string', 'name': 'name', 'type': 'string'},
            {
                'internalType': 'address',
                'name': 'implementation',
                'type': 'address',
            },
            {
                'internalType': 'bool',
                'name': 'enforceWhitelist',
                'type': 'bool',
            },
            {
                'internalType': 'uint256',
                'name': 'closeFactor',
                'type': 'uint256',
            },
            {
                'internalType': 'uint256',
                'name': 'liquidationIncentive',
                'type': 'uint256',
            },
            {
                'internalType': 'address',
                'name': 'priceOracle',
                'type': 'address',
            },
        ],
        'name': 'deployPool',
        'outputs': [
            {'internalType': 'uint256', 'name': '', 'type': 'uint256'},
            {'internalType': 'address', 'name': '', 'type': 'address'},
        ],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'deployerWhitelist': {
        'inputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'name': 'deployerWhitelist',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'enforceDeployerWhitelist': {
        'inputs': [],
        'name': 'enforceDeployerWhitelist',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'getAllPools': {
        'inputs': [],
        'name': 'getAllPools',
        'outputs': [
            {
                'components': [
                    {
                        'internalType': 'string',
                        'name': 'name',
                        'type': 'string',
                    },
                    {
                        'internalType': 'address',
                        'name': 'creator',
                        'type': 'address',
                    },
                    {
                        'internalType': 'address',
                        'name': 'comptroller',
                        'type': 'address',
                    },
                    {
                        'internalType': 'uint256',
                        'name': 'blockPosted',
                        'type': 'uint256',
                    },
                    {
                        'internalType': 'uint256',
                        'name': 'timestampPosted',
                        'type': 'uint256',
                    },
                ],
                'internalType': 'struct FusePoolDirectory.FusePool[]',
                'name': '',
                'type': 'tuple[]',
            }
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'getBookmarks': {
        'inputs': [
            {'internalType': 'address', 'name': 'account', 'type': 'address'}
        ],
        'name': 'getBookmarks',
        'outputs': [
            {'internalType': 'address[]', 'name': '', 'type': 'address[]'}
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'getPoolsByAccount': {
        'inputs': [
            {'internalType': 'address', 'name': 'account', 'type': 'address'}
        ],
        'name': 'getPoolsByAccount',
        'outputs': [
            {'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'},
            {
                'components': [
                    {
                        'internalType': 'string',
                        'name': 'name',
                        'type': 'string',
                    },
                    {
                        'internalType': 'address',
                        'name': 'creator',
                        'type': 'address',
                    },
                    {
                        'internalType': 'address',
                        'name': 'comptroller',
                        'type': 'address',
                    },
                    {
                        'internalType': 'uint256',
                        'name': 'blockPosted',
                        'type': 'uint256',
                    },
                    {
                        'internalType': 'uint256',
                        'name': 'timestampPosted',
                        'type': 'uint256',
                    },
                ],
                'internalType': 'struct FusePoolDirectory.FusePool[]',
                'name': '',
                'type': 'tuple[]',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'getPublicPools': {
        'inputs': [],
        'name': 'getPublicPools',
        'outputs': [
            {'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'},
            {
                'components': [
                    {
                        'internalType': 'string',
                        'name': 'name',
                        'type': 'string',
                    },
                    {
                        'internalType': 'address',
                        'name': 'creator',
                        'type': 'address',
                    },
                    {
                        'internalType': 'address',
                        'name': 'comptroller',
                        'type': 'address',
                    },
                    {
                        'internalType': 'uint256',
                        'name': 'blockPosted',
                        'type': 'uint256',
                    },
                    {
                        'internalType': 'uint256',
                        'name': 'timestampPosted',
                        'type': 'uint256',
                    },
                ],
                'internalType': 'struct FusePoolDirectory.FusePool[]',
                'name': '',
                'type': 'tuple[]',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'getPublicPoolsByVerification': {
        'inputs': [
            {'internalType': 'bool', 'name': 'whitelistedAdmin', 'type': 'bool'}
        ],
        'name': 'getPublicPoolsByVerification',
        'outputs': [
            {'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'},
            {
                'components': [
                    {
                        'internalType': 'string',
                        'name': 'name',
                        'type': 'string',
                    },
                    {
                        'internalType': 'address',
                        'name': 'creator',
                        'type': 'address',
                    },
                    {
                        'internalType': 'address',
                        'name': 'comptroller',
                        'type': 'address',
                    },
                    {
                        'internalType': 'uint256',
                        'name': 'blockPosted',
                        'type': 'uint256',
                    },
                    {
                        'internalType': 'uint256',
                        'name': 'timestampPosted',
                        'type': 'uint256',
                    },
                ],
                'internalType': 'struct FusePoolDirectory.FusePool[]',
                'name': '',
                'type': 'tuple[]',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'initialize': {
        'inputs': [
            {
                'internalType': 'bool',
                'name': '_enforceDeployerWhitelist',
                'type': 'bool',
            },
            {
                'internalType': 'address[]',
                'name': '_deployerWhitelist',
                'type': 'address[]',
            },
        ],
        'name': 'initialize',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'owner': {
        'inputs': [],
        'name': 'owner',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'poolExists': {
        'inputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'name': 'poolExists',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'pools': {
        'inputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'name': 'pools',
        'outputs': [
            {'internalType': 'string', 'name': 'name', 'type': 'string'},
            {'internalType': 'address', 'name': 'creator', 'type': 'address'},
            {
                'internalType': 'address',
                'name': 'comptroller',
                'type': 'address',
            },
            {
                'internalType': 'uint256',
                'name': 'blockPosted',
                'type': 'uint256',
            },
            {
                'internalType': 'uint256',
                'name': 'timestampPosted',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'renounceOwnership': {
        'inputs': [],
        'name': 'renounceOwnership',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'setPoolName': {
        'inputs': [
            {'internalType': 'uint256', 'name': 'index', 'type': 'uint256'},
            {'internalType': 'string', 'name': 'name', 'type': 'string'},
        ],
        'name': 'setPoolName',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'transferOwnership': {
        'inputs': [
            {'internalType': 'address', 'name': 'newOwner', 'type': 'address'}
        ],
        'name': 'transferOwnership',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
}


comptroller_abis = {
    'ActionPaused': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'contract CToken',
                'name': 'cToken',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'string',
                'name': 'action',
                'type': 'string',
            },
            {
                'indexed': False,
                'internalType': 'bool',
                'name': 'pauseState',
                'type': 'bool',
            },
        ],
        'name': 'ActionPaused',
        'type': 'event',
    },
    'AddedRewardsDistributor': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'rewardsDistributor',
                'type': 'address',
            }
        ],
        'name': 'AddedRewardsDistributor',
        'type': 'event',
    },
    'AutoImplementationsToggled': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'bool',
                'name': 'enabled',
                'type': 'bool',
            }
        ],
        'name': 'AutoImplementationsToggled',
        'type': 'event',
    },
    'Failure': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'error',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'info',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'detail',
                'type': 'uint256',
            },
        ],
        'name': 'Failure',
        'type': 'event',
    },
    'MarketEntered': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'contract CToken',
                'name': 'cToken',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'account',
                'type': 'address',
            },
        ],
        'name': 'MarketEntered',
        'type': 'event',
    },
    'MarketExited': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'contract CToken',
                'name': 'cToken',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'account',
                'type': 'address',
            },
        ],
        'name': 'MarketExited',
        'type': 'event',
    },
    'MarketListed': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'contract CToken',
                'name': 'cToken',
                'type': 'address',
            }
        ],
        'name': 'MarketListed',
        'type': 'event',
    },
    'MarketUnlisted': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'contract CToken',
                'name': 'cToken',
                'type': 'address',
            }
        ],
        'name': 'MarketUnlisted',
        'type': 'event',
    },
    'NewBorrowCap': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'contract CToken',
                'name': 'cToken',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'newBorrowCap',
                'type': 'uint256',
            },
        ],
        'name': 'NewBorrowCap',
        'type': 'event',
    },
    'NewBorrowCapGuardian': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'oldBorrowCapGuardian',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'newBorrowCapGuardian',
                'type': 'address',
            },
        ],
        'name': 'NewBorrowCapGuardian',
        'type': 'event',
    },
    'NewCloseFactor': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'oldCloseFactorMantissa',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'newCloseFactorMantissa',
                'type': 'uint256',
            },
        ],
        'name': 'NewCloseFactor',
        'type': 'event',
    },
    'NewCollateralFactor': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'contract CToken',
                'name': 'cToken',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'oldCollateralFactorMantissa',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'newCollateralFactorMantissa',
                'type': 'uint256',
            },
        ],
        'name': 'NewCollateralFactor',
        'type': 'event',
    },
    'NewLiquidationIncentive': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'oldLiquidationIncentiveMantissa',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'newLiquidationIncentiveMantissa',
                'type': 'uint256',
            },
        ],
        'name': 'NewLiquidationIncentive',
        'type': 'event',
    },
    'NewPauseGuardian': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'oldPauseGuardian',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'newPauseGuardian',
                'type': 'address',
            },
        ],
        'name': 'NewPauseGuardian',
        'type': 'event',
    },
    'NewPriceOracle': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'contract PriceOracle',
                'name': 'oldPriceOracle',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'contract PriceOracle',
                'name': 'newPriceOracle',
                'type': 'address',
            },
        ],
        'name': 'NewPriceOracle',
        'type': 'event',
    },
    'NewSupplyCap': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'contract CToken',
                'name': 'cToken',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'newSupplyCap',
                'type': 'uint256',
            },
        ],
        'name': 'NewSupplyCap',
        'type': 'event',
    },
    'WhitelistEnforcementChanged': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'bool',
                'name': 'enforce',
                'type': 'bool',
            }
        ],
        'name': 'WhitelistEnforcementChanged',
        'type': 'event',
    },
    '_addRewardsDistributor': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'address',
                'name': 'distributor',
                'type': 'address',
            }
        ],
        'name': '_addRewardsDistributor',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_afterNonReentrant': {
        'constant': False,
        'inputs': [],
        'name': '_afterNonReentrant',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_become': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'contract Unitroller',
                'name': 'unitroller',
                'type': 'address',
            }
        ],
        'name': '_become',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_becomeImplementation': {
        'constant': False,
        'inputs': [],
        'name': '_becomeImplementation',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_beforeNonReentrant': {
        'constant': False,
        'inputs': [],
        'name': '_beforeNonReentrant',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_borrowGuardianPaused': {
        'constant': True,
        'inputs': [],
        'name': '_borrowGuardianPaused',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    '_deployMarket': {
        'constant': False,
        'inputs': [
            {'internalType': 'bool', 'name': 'isCEther', 'type': 'bool'},
            {
                'internalType': 'bytes',
                'name': 'constructorData',
                'type': 'bytes',
            },
            {
                'internalType': 'uint256',
                'name': 'collateralFactorMantissa',
                'type': 'uint256',
            },
        ],
        'name': '_deployMarket',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_mintGuardianPaused': {
        'constant': True,
        'inputs': [],
        'name': '_mintGuardianPaused',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    '_setBorrowCapGuardian': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'address',
                'name': 'newBorrowCapGuardian',
                'type': 'address',
            }
        ],
        'name': '_setBorrowCapGuardian',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setBorrowPaused': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'contract CToken',
                'name': 'cToken',
                'type': 'address',
            },
            {'internalType': 'bool', 'name': 'state', 'type': 'bool'},
        ],
        'name': '_setBorrowPaused',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setCloseFactor': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'newCloseFactorMantissa',
                'type': 'uint256',
            }
        ],
        'name': '_setCloseFactor',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setCollateralFactor': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'contract CToken',
                'name': 'cToken',
                'type': 'address',
            },
            {
                'internalType': 'uint256',
                'name': 'newCollateralFactorMantissa',
                'type': 'uint256',
            },
        ],
        'name': '_setCollateralFactor',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setLiquidationIncentive': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'newLiquidationIncentiveMantissa',
                'type': 'uint256',
            }
        ],
        'name': '_setLiquidationIncentive',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setMarketBorrowCaps': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'contract CToken[]',
                'name': 'cTokens',
                'type': 'address[]',
            },
            {
                'internalType': 'uint256[]',
                'name': 'newBorrowCaps',
                'type': 'uint256[]',
            },
        ],
        'name': '_setMarketBorrowCaps',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setMarketSupplyCaps': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'contract CToken[]',
                'name': 'cTokens',
                'type': 'address[]',
            },
            {
                'internalType': 'uint256[]',
                'name': 'newSupplyCaps',
                'type': 'uint256[]',
            },
        ],
        'name': '_setMarketSupplyCaps',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setMintPaused': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'contract CToken',
                'name': 'cToken',
                'type': 'address',
            },
            {'internalType': 'bool', 'name': 'state', 'type': 'bool'},
        ],
        'name': '_setMintPaused',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setPauseGuardian': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'address',
                'name': 'newPauseGuardian',
                'type': 'address',
            }
        ],
        'name': '_setPauseGuardian',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setPriceOracle': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'contract PriceOracle',
                'name': 'newOracle',
                'type': 'address',
            }
        ],
        'name': '_setPriceOracle',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setSeizePaused': {
        'constant': False,
        'inputs': [{'internalType': 'bool', 'name': 'state', 'type': 'bool'}],
        'name': '_setSeizePaused',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setTransferPaused': {
        'constant': False,
        'inputs': [{'internalType': 'bool', 'name': 'state', 'type': 'bool'}],
        'name': '_setTransferPaused',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setWhitelistEnforcement': {
        'constant': False,
        'inputs': [{'internalType': 'bool', 'name': 'enforce', 'type': 'bool'}],
        'name': '_setWhitelistEnforcement',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setWhitelistStatuses': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'address[]',
                'name': 'suppliers',
                'type': 'address[]',
            },
            {'internalType': 'bool[]', 'name': 'statuses', 'type': 'bool[]'},
        ],
        'name': '_setWhitelistStatuses',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_toggleAutoImplementations': {
        'constant': False,
        'inputs': [{'internalType': 'bool', 'name': 'enabled', 'type': 'bool'}],
        'name': '_toggleAutoImplementations',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_unsupportMarket': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'contract CToken',
                'name': 'cToken',
                'type': 'address',
            }
        ],
        'name': '_unsupportMarket',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'accountAssets': {
        'constant': True,
        'inputs': [
            {'internalType': 'address', 'name': '', 'type': 'address'},
            {'internalType': 'uint256', 'name': '', 'type': 'uint256'},
        ],
        'name': 'accountAssets',
        'outputs': [
            {'internalType': 'contract CToken', 'name': '', 'type': 'address'}
        ],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'admin': {
        'constant': True,
        'inputs': [],
        'name': 'admin',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'adminHasRights': {
        'constant': True,
        'inputs': [],
        'name': 'adminHasRights',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'allBorrowers': {
        'constant': True,
        'inputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'name': 'allBorrowers',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'allMarkets': {
        'constant': True,
        'inputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'name': 'allMarkets',
        'outputs': [
            {'internalType': 'contract CToken', 'name': '', 'type': 'address'}
        ],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'autoImplementation': {
        'constant': True,
        'inputs': [],
        'name': 'autoImplementation',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'borrowAllowed': {
        'constant': False,
        'inputs': [
            {'internalType': 'address', 'name': 'cToken', 'type': 'address'},
            {'internalType': 'address', 'name': 'borrower', 'type': 'address'},
            {
                'internalType': 'uint256',
                'name': 'borrowAmount',
                'type': 'uint256',
            },
        ],
        'name': 'borrowAllowed',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'borrowCapGuardian': {
        'constant': True,
        'inputs': [],
        'name': 'borrowCapGuardian',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'borrowCaps': {
        'constant': True,
        'inputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'name': 'borrowCaps',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'borrowGuardianPaused': {
        'constant': True,
        'inputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'name': 'borrowGuardianPaused',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'borrowVerify': {
        'constant': False,
        'inputs': [
            {'internalType': 'address', 'name': 'cToken', 'type': 'address'},
            {'internalType': 'address', 'name': 'borrower', 'type': 'address'},
            {
                'internalType': 'uint256',
                'name': 'borrowAmount',
                'type': 'uint256',
            },
        ],
        'name': 'borrowVerify',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'borrowWithinLimits': {
        'constant': False,
        'inputs': [
            {'internalType': 'address', 'name': 'cToken', 'type': 'address'},
            {
                'internalType': 'uint256',
                'name': 'accountBorrowsNew',
                'type': 'uint256',
            },
        ],
        'name': 'borrowWithinLimits',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'cTokensByUnderlying': {
        'constant': True,
        'inputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'name': 'cTokensByUnderlying',
        'outputs': [
            {'internalType': 'contract CToken', 'name': '', 'type': 'address'}
        ],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'checkMembership': {
        'constant': True,
        'inputs': [
            {'internalType': 'address', 'name': 'account', 'type': 'address'},
            {
                'internalType': 'contract CToken',
                'name': 'cToken',
                'type': 'address',
            },
        ],
        'name': 'checkMembership',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'closeFactorMantissa': {
        'constant': True,
        'inputs': [],
        'name': 'closeFactorMantissa',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'comptrollerImplementation': {
        'constant': True,
        'inputs': [],
        'name': 'comptrollerImplementation',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'enforceWhitelist': {
        'constant': True,
        'inputs': [],
        'name': 'enforceWhitelist',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'enterMarkets': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'address[]',
                'name': 'cTokens',
                'type': 'address[]',
            }
        ],
        'name': 'enterMarkets',
        'outputs': [
            {'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'}
        ],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'exitMarket': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'address',
                'name': 'cTokenAddress',
                'type': 'address',
            }
        ],
        'name': 'exitMarket',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'fuseAdminHasRights': {
        'constant': True,
        'inputs': [],
        'name': 'fuseAdminHasRights',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'getAccountLiquidity': {
        'constant': True,
        'inputs': [
            {'internalType': 'address', 'name': 'account', 'type': 'address'}
        ],
        'name': 'getAccountLiquidity',
        'outputs': [
            {'internalType': 'uint256', 'name': '', 'type': 'uint256'},
            {'internalType': 'uint256', 'name': '', 'type': 'uint256'},
            {'internalType': 'uint256', 'name': '', 'type': 'uint256'},
        ],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'getAllBorrowers': {
        'constant': True,
        'inputs': [],
        'name': 'getAllBorrowers',
        'outputs': [
            {'internalType': 'address[]', 'name': '', 'type': 'address[]'}
        ],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'getAllMarkets': {
        'constant': True,
        'inputs': [],
        'name': 'getAllMarkets',
        'outputs': [
            {
                'internalType': 'contract CToken[]',
                'name': '',
                'type': 'address[]',
            }
        ],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'getAssetsIn': {
        'constant': True,
        'inputs': [
            {'internalType': 'address', 'name': 'account', 'type': 'address'}
        ],
        'name': 'getAssetsIn',
        'outputs': [
            {
                'internalType': 'contract CToken[]',
                'name': '',
                'type': 'address[]',
            }
        ],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'getHypotheticalAccountLiquidity': {
        'constant': True,
        'inputs': [
            {'internalType': 'address', 'name': 'account', 'type': 'address'},
            {
                'internalType': 'address',
                'name': 'cTokenModify',
                'type': 'address',
            },
            {
                'internalType': 'uint256',
                'name': 'redeemTokens',
                'type': 'uint256',
            },
            {
                'internalType': 'uint256',
                'name': 'borrowAmount',
                'type': 'uint256',
            },
        ],
        'name': 'getHypotheticalAccountLiquidity',
        'outputs': [
            {'internalType': 'uint256', 'name': '', 'type': 'uint256'},
            {'internalType': 'uint256', 'name': '', 'type': 'uint256'},
            {'internalType': 'uint256', 'name': '', 'type': 'uint256'},
        ],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'getRewardsDistributors': {
        'constant': True,
        'inputs': [],
        'name': 'getRewardsDistributors',
        'outputs': [
            {'internalType': 'address[]', 'name': '', 'type': 'address[]'}
        ],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'getWhitelist': {
        'constant': True,
        'inputs': [],
        'name': 'getWhitelist',
        'outputs': [
            {'internalType': 'address[]', 'name': '', 'type': 'address[]'}
        ],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'isComptroller': {
        'constant': True,
        'inputs': [],
        'name': 'isComptroller',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'isDeprecated': {
        'constant': True,
        'inputs': [
            {
                'internalType': 'contract CToken',
                'name': 'cToken',
                'type': 'address',
            }
        ],
        'name': 'isDeprecated',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'liquidateBorrowAllowed': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'address',
                'name': 'cTokenBorrowed',
                'type': 'address',
            },
            {
                'internalType': 'address',
                'name': 'cTokenCollateral',
                'type': 'address',
            },
            {
                'internalType': 'address',
                'name': 'liquidator',
                'type': 'address',
            },
            {'internalType': 'address', 'name': 'borrower', 'type': 'address'},
            {
                'internalType': 'uint256',
                'name': 'repayAmount',
                'type': 'uint256',
            },
        ],
        'name': 'liquidateBorrowAllowed',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'liquidateBorrowVerify': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'address',
                'name': 'cTokenBorrowed',
                'type': 'address',
            },
            {
                'internalType': 'address',
                'name': 'cTokenCollateral',
                'type': 'address',
            },
            {
                'internalType': 'address',
                'name': 'liquidator',
                'type': 'address',
            },
            {'internalType': 'address', 'name': 'borrower', 'type': 'address'},
            {
                'internalType': 'uint256',
                'name': 'actualRepayAmount',
                'type': 'uint256',
            },
            {
                'internalType': 'uint256',
                'name': 'seizeTokens',
                'type': 'uint256',
            },
        ],
        'name': 'liquidateBorrowVerify',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'liquidateCalculateSeizeTokens': {
        'constant': True,
        'inputs': [
            {
                'internalType': 'address',
                'name': 'cTokenBorrowed',
                'type': 'address',
            },
            {
                'internalType': 'address',
                'name': 'cTokenCollateral',
                'type': 'address',
            },
            {
                'internalType': 'uint256',
                'name': 'actualRepayAmount',
                'type': 'uint256',
            },
        ],
        'name': 'liquidateCalculateSeizeTokens',
        'outputs': [
            {'internalType': 'uint256', 'name': '', 'type': 'uint256'},
            {'internalType': 'uint256', 'name': '', 'type': 'uint256'},
        ],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'liquidationIncentiveMantissa': {
        'constant': True,
        'inputs': [],
        'name': 'liquidationIncentiveMantissa',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'markets': {
        'constant': True,
        'inputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'name': 'markets',
        'outputs': [
            {'internalType': 'bool', 'name': 'isListed', 'type': 'bool'},
            {
                'internalType': 'uint256',
                'name': 'collateralFactorMantissa',
                'type': 'uint256',
            },
        ],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'mintAllowed': {
        'constant': False,
        'inputs': [
            {'internalType': 'address', 'name': 'cToken', 'type': 'address'},
            {'internalType': 'address', 'name': 'minter', 'type': 'address'},
            {
                'internalType': 'uint256',
                'name': 'mintAmount',
                'type': 'uint256',
            },
        ],
        'name': 'mintAllowed',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'mintGuardianPaused': {
        'constant': True,
        'inputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'name': 'mintGuardianPaused',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'mintVerify': {
        'constant': False,
        'inputs': [
            {'internalType': 'address', 'name': 'cToken', 'type': 'address'},
            {'internalType': 'address', 'name': 'minter', 'type': 'address'},
            {
                'internalType': 'uint256',
                'name': 'actualMintAmount',
                'type': 'uint256',
            },
            {
                'internalType': 'uint256',
                'name': 'mintTokens',
                'type': 'uint256',
            },
        ],
        'name': 'mintVerify',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'mintWithinLimits': {
        'constant': False,
        'inputs': [
            {'internalType': 'address', 'name': 'cToken', 'type': 'address'},
            {
                'internalType': 'uint256',
                'name': 'exchangeRateMantissa',
                'type': 'uint256',
            },
            {
                'internalType': 'uint256',
                'name': 'accountTokens',
                'type': 'uint256',
            },
            {
                'internalType': 'uint256',
                'name': 'mintAmount',
                'type': 'uint256',
            },
        ],
        'name': 'mintWithinLimits',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'oracle': {
        'constant': True,
        'inputs': [],
        'name': 'oracle',
        'outputs': [
            {
                'internalType': 'contract PriceOracle',
                'name': '',
                'type': 'address',
            }
        ],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'pauseGuardian': {
        'constant': True,
        'inputs': [],
        'name': 'pauseGuardian',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'pendingAdmin': {
        'constant': True,
        'inputs': [],
        'name': 'pendingAdmin',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'pendingComptrollerImplementation': {
        'constant': True,
        'inputs': [],
        'name': 'pendingComptrollerImplementation',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'redeemAllowed': {
        'constant': False,
        'inputs': [
            {'internalType': 'address', 'name': 'cToken', 'type': 'address'},
            {'internalType': 'address', 'name': 'redeemer', 'type': 'address'},
            {
                'internalType': 'uint256',
                'name': 'redeemTokens',
                'type': 'uint256',
            },
        ],
        'name': 'redeemAllowed',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'redeemVerify': {
        'constant': False,
        'inputs': [
            {'internalType': 'address', 'name': 'cToken', 'type': 'address'},
            {'internalType': 'address', 'name': 'redeemer', 'type': 'address'},
            {
                'internalType': 'uint256',
                'name': 'redeemAmount',
                'type': 'uint256',
            },
            {
                'internalType': 'uint256',
                'name': 'redeemTokens',
                'type': 'uint256',
            },
        ],
        'name': 'redeemVerify',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'repayBorrowAllowed': {
        'constant': False,
        'inputs': [
            {'internalType': 'address', 'name': 'cToken', 'type': 'address'},
            {'internalType': 'address', 'name': 'payer', 'type': 'address'},
            {'internalType': 'address', 'name': 'borrower', 'type': 'address'},
            {
                'internalType': 'uint256',
                'name': 'repayAmount',
                'type': 'uint256',
            },
        ],
        'name': 'repayBorrowAllowed',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'repayBorrowVerify': {
        'constant': False,
        'inputs': [
            {'internalType': 'address', 'name': 'cToken', 'type': 'address'},
            {'internalType': 'address', 'name': 'payer', 'type': 'address'},
            {'internalType': 'address', 'name': 'borrower', 'type': 'address'},
            {
                'internalType': 'uint256',
                'name': 'actualRepayAmount',
                'type': 'uint256',
            },
            {
                'internalType': 'uint256',
                'name': 'borrowerIndex',
                'type': 'uint256',
            },
        ],
        'name': 'repayBorrowVerify',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'rewardsDistributors': {
        'constant': True,
        'inputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'name': 'rewardsDistributors',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'seizeAllowed': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'address',
                'name': 'cTokenCollateral',
                'type': 'address',
            },
            {
                'internalType': 'address',
                'name': 'cTokenBorrowed',
                'type': 'address',
            },
            {
                'internalType': 'address',
                'name': 'liquidator',
                'type': 'address',
            },
            {'internalType': 'address', 'name': 'borrower', 'type': 'address'},
            {
                'internalType': 'uint256',
                'name': 'seizeTokens',
                'type': 'uint256',
            },
        ],
        'name': 'seizeAllowed',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'seizeGuardianPaused': {
        'constant': True,
        'inputs': [],
        'name': 'seizeGuardianPaused',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'seizeVerify': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'address',
                'name': 'cTokenCollateral',
                'type': 'address',
            },
            {
                'internalType': 'address',
                'name': 'cTokenBorrowed',
                'type': 'address',
            },
            {
                'internalType': 'address',
                'name': 'liquidator',
                'type': 'address',
            },
            {'internalType': 'address', 'name': 'borrower', 'type': 'address'},
            {
                'internalType': 'uint256',
                'name': 'seizeTokens',
                'type': 'uint256',
            },
        ],
        'name': 'seizeVerify',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'suppliers': {
        'constant': True,
        'inputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'name': 'suppliers',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'supplyCaps': {
        'constant': True,
        'inputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'name': 'supplyCaps',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'transferAllowed': {
        'constant': False,
        'inputs': [
            {'internalType': 'address', 'name': 'cToken', 'type': 'address'},
            {'internalType': 'address', 'name': 'src', 'type': 'address'},
            {'internalType': 'address', 'name': 'dst', 'type': 'address'},
            {
                'internalType': 'uint256',
                'name': 'transferTokens',
                'type': 'uint256',
            },
        ],
        'name': 'transferAllowed',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'transferGuardianPaused': {
        'constant': True,
        'inputs': [],
        'name': 'transferGuardianPaused',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'transferVerify': {
        'constant': False,
        'inputs': [
            {'internalType': 'address', 'name': 'cToken', 'type': 'address'},
            {'internalType': 'address', 'name': 'src', 'type': 'address'},
            {'internalType': 'address', 'name': 'dst', 'type': 'address'},
            {
                'internalType': 'uint256',
                'name': 'transferTokens',
                'type': 'uint256',
            },
        ],
        'name': 'transferVerify',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'whitelist': {
        'constant': True,
        'inputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'name': 'whitelist',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'whitelistArray': {
        'constant': True,
        'inputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'name': 'whitelistArray',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
}

ctoken_function_abis = {
    '_setImplementation': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'address',
                'name': 'implementation_',
                'type': 'address',
            },
            {'internalType': 'bool', 'name': 'allowResign', 'type': 'bool'},
            {
                'internalType': 'bytes',
                'name': 'becomeImplementationData',
                'type': 'bytes',
            },
        ],
        'name': '_setImplementation',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'admin': {
        'constant': True,
        'inputs': [],
        'name': 'admin',
        'outputs': [
            {'internalType': 'address payable', 'name': '', 'type': 'address'}
        ],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'adminHasRights': {
        'constant': True,
        'inputs': [],
        'name': 'adminHasRights',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'delegateToImplementation': {
        'constant': False,
        'inputs': [{'internalType': 'bytes', 'name': 'data', 'type': 'bytes'}],
        'name': 'delegateToImplementation',
        'outputs': [{'internalType': 'bytes', 'name': '', 'type': 'bytes'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'fuseAdminHasRights': {
        'constant': True,
        'inputs': [],
        'name': 'fuseAdminHasRights',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'implementation': {
        'constant': True,
        'inputs': [],
        'name': 'implementation',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    '_acceptAdmin': {
        'constant': False,
        'inputs': [],
        'name': '_acceptAdmin',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_addReserves': {
        'constant': False,
        'inputs': [
            {'internalType': 'uint256', 'name': 'addAmount', 'type': 'uint256'}
        ],
        'name': '_addReserves',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_becomeImplementation': {
        'constant': False,
        'inputs': [{'internalType': 'bytes', 'name': 'data', 'type': 'bytes'}],
        'name': '_becomeImplementation',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_reduceReserves': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'reduceAmount',
                'type': 'uint256',
            }
        ],
        'name': '_reduceReserves',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_renounceAdminRights': {
        'constant': False,
        'inputs': [],
        'name': '_renounceAdminRights',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_renounceFuseAdminRights': {
        'constant': False,
        'inputs': [],
        'name': '_renounceFuseAdminRights',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_resignImplementation': {
        'constant': False,
        'inputs': [],
        'name': '_resignImplementation',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setAdminFee': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'newAdminFeeMantissa',
                'type': 'uint256',
            }
        ],
        'name': '_setAdminFee',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setComptroller': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'contract ComptrollerInterface',
                'name': 'newComptroller',
                'type': 'address',
            }
        ],
        'name': '_setComptroller',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setFuseFee': {
        'constant': False,
        'inputs': [],
        'name': '_setFuseFee',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setInterestRateModel': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'contract InterestRateModel',
                'name': 'newInterestRateModel',
                'type': 'address',
            }
        ],
        'name': '_setInterestRateModel',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setPendingAdmin': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'address payable',
                'name': 'newPendingAdmin',
                'type': 'address',
            }
        ],
        'name': '_setPendingAdmin',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_setReserveFactor': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'newReserveFactorMantissa',
                'type': 'uint256',
            }
        ],
        'name': '_setReserveFactor',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_withdrawAdminFees': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'withdrawAmount',
                'type': 'uint256',
            }
        ],
        'name': '_withdrawAdminFees',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    '_withdrawFuseFees': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'withdrawAmount',
                'type': 'uint256',
            }
        ],
        'name': '_withdrawFuseFees',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'accrualBlockNumber': {
        'constant': True,
        'inputs': [],
        'name': 'accrualBlockNumber',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'accrueInterest': {
        'constant': False,
        'inputs': [],
        'name': 'accrueInterest',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'adminFeeMantissa': {
        'constant': True,
        'inputs': [],
        'name': 'adminFeeMantissa',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'allowance': {
        'constant': True,
        'inputs': [
            {'internalType': 'address', 'name': 'owner', 'type': 'address'},
            {'internalType': 'address', 'name': 'spender', 'type': 'address'},
        ],
        'name': 'allowance',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'approve': {
        'constant': False,
        'inputs': [
            {'internalType': 'address', 'name': 'spender', 'type': 'address'},
            {'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'},
        ],
        'name': 'approve',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'balanceOf': {
        'constant': True,
        'inputs': [
            {'internalType': 'address', 'name': 'owner', 'type': 'address'}
        ],
        'name': 'balanceOf',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'balanceOfUnderlying': {
        'constant': False,
        'inputs': [
            {'internalType': 'address', 'name': 'owner', 'type': 'address'}
        ],
        'name': 'balanceOfUnderlying',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'borrow': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'borrowAmount',
                'type': 'uint256',
            }
        ],
        'name': 'borrow',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'borrowBalanceCurrent': {
        'constant': False,
        'inputs': [
            {'internalType': 'address', 'name': 'account', 'type': 'address'}
        ],
        'name': 'borrowBalanceCurrent',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'borrowBalanceStored': {
        'constant': True,
        'inputs': [
            {'internalType': 'address', 'name': 'account', 'type': 'address'}
        ],
        'name': 'borrowBalanceStored',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'borrowIndex': {
        'constant': True,
        'inputs': [],
        'name': 'borrowIndex',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'borrowRatePerBlock': {
        'constant': True,
        'inputs': [],
        'name': 'borrowRatePerBlock',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'comptroller': {
        'constant': True,
        'inputs': [],
        'name': 'comptroller',
        'outputs': [
            {
                'internalType': 'contract ComptrollerInterface',
                'name': '',
                'type': 'address',
            }
        ],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'decimals': {
        'constant': True,
        'inputs': [],
        'name': 'decimals',
        'outputs': [{'internalType': 'uint8', 'name': '', 'type': 'uint8'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'exchangeRateCurrent': {
        'constant': False,
        'inputs': [],
        'name': 'exchangeRateCurrent',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'exchangeRateStored': {
        'constant': True,
        'inputs': [],
        'name': 'exchangeRateStored',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'fuseFeeMantissa': {
        'constant': True,
        'inputs': [],
        'name': 'fuseFeeMantissa',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'getAccountSnapshot': {
        'constant': True,
        'inputs': [
            {'internalType': 'address', 'name': 'account', 'type': 'address'}
        ],
        'name': 'getAccountSnapshot',
        'outputs': [
            {'internalType': 'uint256', 'name': '', 'type': 'uint256'},
            {'internalType': 'uint256', 'name': '', 'type': 'uint256'},
            {'internalType': 'uint256', 'name': '', 'type': 'uint256'},
            {'internalType': 'uint256', 'name': '', 'type': 'uint256'},
        ],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'getCash': {
        'constant': True,
        'inputs': [],
        'name': 'getCash',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'initialize': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'address',
                'name': 'underlying_',
                'type': 'address',
            },
            {
                'internalType': 'contract ComptrollerInterface',
                'name': 'comptroller_',
                'type': 'address',
            },
            {
                'internalType': 'contract InterestRateModel',
                'name': 'interestRateModel_',
                'type': 'address',
            },
            {
                'internalType': 'uint256',
                'name': 'initialExchangeRateMantissa_',
                'type': 'uint256',
            },
            {'internalType': 'string', 'name': 'name_', 'type': 'string'},
            {'internalType': 'string', 'name': 'symbol_', 'type': 'string'},
            {'internalType': 'uint8', 'name': 'decimals_', 'type': 'uint8'},
            {
                'internalType': 'uint256',
                'name': 'reserveFactorMantissa_',
                'type': 'uint256',
            },
            {
                'internalType': 'uint256',
                'name': 'adminFeeMantissa_',
                'type': 'uint256',
            },
        ],
        'name': 'initialize',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'interestRateModel': {
        'constant': True,
        'inputs': [],
        'name': 'interestRateModel',
        'outputs': [
            {
                'internalType': 'contract InterestRateModel',
                'name': '',
                'type': 'address',
            }
        ],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'isCEther': {
        'constant': True,
        'inputs': [],
        'name': 'isCEther',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'isCToken': {
        'constant': True,
        'inputs': [],
        'name': 'isCToken',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'liquidateBorrow': {
        'constant': False,
        'inputs': [
            {'internalType': 'address', 'name': 'borrower', 'type': 'address'},
            {
                'internalType': 'uint256',
                'name': 'repayAmount',
                'type': 'uint256',
            },
            {
                'internalType': 'contract CTokenInterface',
                'name': 'cTokenCollateral',
                'type': 'address',
            },
        ],
        'name': 'liquidateBorrow',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'mint': {
        'constant': False,
        'inputs': [
            {'internalType': 'uint256', 'name': 'mintAmount', 'type': 'uint256'}
        ],
        'name': 'mint',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'name': {
        'constant': True,
        'inputs': [],
        'name': 'name',
        'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'pendingAdmin': {
        'constant': True,
        'inputs': [],
        'name': 'pendingAdmin',
        'outputs': [
            {'internalType': 'address payable', 'name': '', 'type': 'address'}
        ],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'redeem': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'redeemTokens',
                'type': 'uint256',
            }
        ],
        'name': 'redeem',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'redeemUnderlying': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'redeemAmount',
                'type': 'uint256',
            }
        ],
        'name': 'redeemUnderlying',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'repayBorrow': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'repayAmount',
                'type': 'uint256',
            }
        ],
        'name': 'repayBorrow',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'repayBorrowBehalf': {
        'constant': False,
        'inputs': [
            {'internalType': 'address', 'name': 'borrower', 'type': 'address'},
            {
                'internalType': 'uint256',
                'name': 'repayAmount',
                'type': 'uint256',
            },
        ],
        'name': 'repayBorrowBehalf',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'reserveFactorMantissa': {
        'constant': True,
        'inputs': [],
        'name': 'reserveFactorMantissa',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'seize': {
        'constant': False,
        'inputs': [
            {
                'internalType': 'address',
                'name': 'liquidator',
                'type': 'address',
            },
            {'internalType': 'address', 'name': 'borrower', 'type': 'address'},
            {
                'internalType': 'uint256',
                'name': 'seizeTokens',
                'type': 'uint256',
            },
        ],
        'name': 'seize',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'supplyRatePerBlock': {
        'constant': True,
        'inputs': [],
        'name': 'supplyRatePerBlock',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'symbol': {
        'constant': True,
        'inputs': [],
        'name': 'symbol',
        'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'totalAdminFees': {
        'constant': True,
        'inputs': [],
        'name': 'totalAdminFees',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'totalBorrows': {
        'constant': True,
        'inputs': [],
        'name': 'totalBorrows',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'totalBorrowsCurrent': {
        'constant': False,
        'inputs': [],
        'name': 'totalBorrowsCurrent',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'totalFuseFees': {
        'constant': True,
        'inputs': [],
        'name': 'totalFuseFees',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'totalReserves': {
        'constant': True,
        'inputs': [],
        'name': 'totalReserves',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'totalSupply': {
        'constant': True,
        'inputs': [],
        'name': 'totalSupply',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'transfer': {
        'constant': False,
        'inputs': [
            {'internalType': 'address', 'name': 'dst', 'type': 'address'},
            {'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'},
        ],
        'name': 'transfer',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'transferFrom': {
        'constant': False,
        'inputs': [
            {'internalType': 'address', 'name': 'src', 'type': 'address'},
            {'internalType': 'address', 'name': 'dst', 'type': 'address'},
            {'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'},
        ],
        'name': 'transferFrom',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'underlying': {
        'constant': True,
        'inputs': [],
        'name': 'underlying',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
}


interest_rate_model_abis = {
    'baseRatePerBlock': {
        'constant': True,
        'inputs': [],
        'name': 'baseRatePerBlock',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'blocksPerYear': {
        'constant': True,
        'inputs': [],
        'name': 'blocksPerYear',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'getBorrowRate': {
        'constant': True,
        'inputs': [
            {'internalType': 'uint256', 'name': 'cash', 'type': 'uint256'},
            {'internalType': 'uint256', 'name': 'borrows', 'type': 'uint256'},
            {'internalType': 'uint256', 'name': 'reserves', 'type': 'uint256'},
        ],
        'name': 'getBorrowRate',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'getSupplyRate': {
        'constant': True,
        'inputs': [
            {'internalType': 'uint256', 'name': 'cash', 'type': 'uint256'},
            {'internalType': 'uint256', 'name': 'borrows', 'type': 'uint256'},
            {'internalType': 'uint256', 'name': 'reserves', 'type': 'uint256'},
            {
                'internalType': 'uint256',
                'name': 'reserveFactorMantissa',
                'type': 'uint256',
            },
        ],
        'name': 'getSupplyRate',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'isInterestRateModel': {
        'constant': True,
        'inputs': [],
        'name': 'isInterestRateModel',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'jumpMultiplierPerBlock': {
        'constant': True,
        'inputs': [],
        'name': 'jumpMultiplierPerBlock',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'kink': {
        'constant': True,
        'inputs': [],
        'name': 'kink',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'multiplierPerBlock': {
        'constant': True,
        'inputs': [],
        'name': 'multiplierPerBlock',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'utilizationRate': {
        'constant': True,
        'inputs': [
            {'internalType': 'uint256', 'name': 'cash', 'type': 'uint256'},
            {'internalType': 'uint256', 'name': 'borrows', 'type': 'uint256'},
            {'internalType': 'uint256', 'name': 'reserves', 'type': 'uint256'},
        ],
        'name': 'utilizationRate',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'pure',
        'type': 'function',
    },
}

oracle_abis = {
    'NewAdmin': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'oldAdmin',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'newAdmin',
                'type': 'address',
            },
        ],
        'name': 'NewAdmin',
        'type': 'event',
    },
    'NewDefaultOracle': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'oldOracle',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'newOracle',
                'type': 'address',
            },
        ],
        'name': 'NewDefaultOracle',
        'type': 'event',
    },
    'NewOracle': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'underlying',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'oldOracle',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'newOracle',
                'type': 'address',
            },
        ],
        'name': 'NewOracle',
        'type': 'event',
    },
    'add': {
        'inputs': [
            {
                'internalType': 'address[]',
                'name': 'underlyings',
                'type': 'address[]',
            },
            {
                'internalType': 'contract PriceOracle[]',
                'name': '_oracles',
                'type': 'address[]',
            },
        ],
        'name': 'add',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'admin': {
        'inputs': [],
        'name': 'admin',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'canAdminOverwrite': {
        'inputs': [],
        'name': 'canAdminOverwrite',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'changeAdmin': {
        'inputs': [
            {'internalType': 'address', 'name': 'newAdmin', 'type': 'address'}
        ],
        'name': 'changeAdmin',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'defaultOracle': {
        'inputs': [],
        'name': 'defaultOracle',
        'outputs': [
            {
                'internalType': 'contract PriceOracle',
                'name': '',
                'type': 'address',
            }
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'getUnderlyingPrice': {
        'inputs': [
            {
                'internalType': 'contract CToken',
                'name': 'cToken',
                'type': 'address',
            }
        ],
        'name': 'getUnderlyingPrice',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'initialize': {
        'inputs': [
            {
                'internalType': 'address[]',
                'name': 'underlyings',
                'type': 'address[]',
            },
            {
                'internalType': 'contract PriceOracle[]',
                'name': '_oracles',
                'type': 'address[]',
            },
            {
                'internalType': 'contract PriceOracle',
                'name': '_defaultOracle',
                'type': 'address',
            },
            {'internalType': 'address', 'name': '_admin', 'type': 'address'},
            {
                'internalType': 'bool',
                'name': '_canAdminOverwrite',
                'type': 'bool',
            },
        ],
        'name': 'initialize',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'oracles': {
        'inputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'name': 'oracles',
        'outputs': [
            {
                'internalType': 'contract PriceOracle',
                'name': '',
                'type': 'address',
            }
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'price': {
        'inputs': [
            {'internalType': 'address', 'name': 'underlying', 'type': 'address'}
        ],
        'name': 'price',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'setDefaultOracle': {
        'inputs': [
            {
                'internalType': 'contract PriceOracle',
                'name': 'newOracle',
                'type': 'address',
            }
        ],
        'name': 'setDefaultOracle',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
}

