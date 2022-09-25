
# Changelog

*until version `1.0.0` is reached, will use `0.X.Y` versioning where `X` is for breaking changes / major feature upgrades, and `Y` is for bug fixes / minor feature upgrades*

## 0.3.0

**September 25, 2022**

This is a significant release that includes features such as: sql database integration, refactored documentation, streamlined syntax, performance optimizations, and many new types of data queries. This release also includes lots of small bug fixes and quality-of-life improvements not listed below.

#### DB
- integrate sql db for storing collected data
- create tables for: blocks, contract abis, contract creation blocks, ERC20 metadata, 4byte signatures, and Chainlink feeds
- add flags to functions for whether db should be used
- auto-intake collected data into db by default

#### Documentation
- create external documentation page https://ctc.readthedocs.io/en/latest

#### CLI
- add help messages and examples to each subcommand
- add color to cli output
- optimize cli startup times
- allow all cli commands to use ens names in place of addresses
- add many subcommands including
    - storage, limits, encode, proxy, bytecode, chains, selector
    - `abi decompile` command for decoding ABI of solidity and vyper contracts
    - (see `ctc -h` for proper full list)
    - XX do a diff with 3.10?
- add commands for events, candlestick charting
- add `--json` to many cli commands to output data as json

#### Config
- make configuration file optional by using a default config and looking for RPC provider in `ETH_RPC_URL` env var
- when loading old config versions, attempt to transparently convert it to new config version
- added better config validation
- add shell alias configuration to `ctc setup`

#### Protocols
- new protocol-specific functionality for Gnosis and Etherscan
- add subcommands to previous covered protocols
- use binary search to implement trade-to-price function for Uniswap V3 and other AMMs

#### Data Operations
- new transaction and call data decoding system
- automatically query proxy ABI when querying a contract's ABI
    - if a function ABI or event ABI cannot be found, re-query contract proxy to check for ABI updates
- add functionality for fetching all transactions of a given address
- add functionality for predicting block numbers of future timestamps

#### Testing
- use tox for testing each python version
- create legacy test environment with minimal version of each dependency
- test that all cli commands have examples and test that the examples work
- enforce many coding conventions using tests

#### Performance
- utilize caches and concurrency when possible
- add appropriate rate limits for etherscan and 4byte for scraping

#### Python
- upgrade from `setuptools` / `setup.py` to `flit` / `pyproject.toml`
- use black for all py files in repo
- use strict mode for mypy typing annotations
- reduce number of implicit package dependencies by more than 50%
    - fork `eth-abi` package as `eth-abi-lite` to remove dependence on `eth-abi`, `eth-utils`, `toolz` and `cytools`
    - specify min and max version of each dependency to prevent future backwards incompability

#### Other
- add logging system and allow use of `ctc log` command to follow logs
- populate default data directory with metadata of: 22 networks, >1000 ERC20 tokens, and all Chainlink feeds
- add functions for converting block numbers into timestamps for x-axis labels of plots

### Upgrade Guide

1. Run `pip install -U checkthechain`
2. Run `ctc setup`
3. There are some minor api changes (see below)

#### API Changes

Version `0.3.0` contains some breaking changes to make the API more consistent and intuitive. Care was taken to minimize these breaking changes. Future versions of `ctc` will aim to maximize backward compatilibity as much as possible.

- `config` (running `ctc setup` command will automatically upgrade old config and data directory)
    - new config schema using flat structure instead of nested hierarchy (see `ctc.spec.typedefs.config_types`)
    - new data directory schema that better reflects underlying data relationships (see `ctc.config.upgrade_utils.data_dir_versioning`)
- `directory` deprecated in favor of functions in `config`, `db`, and `evm`
- `evm`
    - `decode_function_output()` arg: `package_named_results` --> `package_named_outputs`
    - `async_get_proxy_address()` --> `async_get_proxy_implementation()`
    - erc20 balance and allowance functions:
        - arg `address` --> `wallet`
        - arg `addresses` --> `wallets`
        - `async_get_erc20_holdings_from_transfers` --> `async_get_erc20_balances_from_transfers`
        - `async_get_block_timestamp()` modes renamed from `before`, `after`, `equal` to `<=`, `>=`, `==`
        - `async_get_erc20_balance_of` --> `async_get_erc20_balance`
        - `async_get_erc20_balance_of_addresses` --> `async_get_erc20_balances_of_addresses`
        - `async_get_erc20s_balance_of` --> `async_get_erc20s_balances`
        - `async_get_erc20_balance_of_by_block` --> `async_get_erc20_balance_by_block`
        - `async_get_erc20s_allowances_by_address` --> `async_get_erc20s_allowances_of_addresses`
- `protocols`
    - `curve_utils.async_get_pool_addresses` --> `curve_utils.async_get_pool_tokens`
    - `rari_utils.get_pool_tvl_and_tvb` --> `rari_utils.async_get_pool_tvl_and_tvb`
    - use for blockwise functions always use `by_block` rather than `per_block`
    - `uniswap_v2_utils.async_get_pool_swaps` --> `uniswap_v2_utils.async_get_pool_trades`
    - functions for querying data from specific DEX's now all use unified a unified DEX syntax and API
- `spec`
    - `ConfigSpec` --> `Config`
    - `PartialConfigSpec` --> `PartialConfig`
    - `ProviderSpec` --> `ProviderReference`
- `toolbox`
    - move `toolbox.amm_utils`, `toolbox.twap_utils`, and `toolbox.lending_utils` under `toolbox.defi_utils`
- `cli`
    - all commands are standardized on `--export` rather than `--output` to specify data export targets
- for functions that print out summary information, instead of using a conventions of `print_<X>()` and `summarize_<X>`, use single convention `print_X()`
- only allow positional arguments for the first two arguments of every function

## 0.2.10

**March 26, 2022**

- add functionality for G-Uni Gelato, multicall
- add Fei yield dashboard analytics
- add commands for ABI summarization
- signficantly improve test coverage

## 0.2.9

**March 18, 2022**

- add Uniswap V3 functionliaty
- improve Chainlink functions, commands, and feed registry
- add twap_utils
- add cli aliases
- many small fixes
- handle various types of non-compliant erc20s

## 0.2.8

**March 2, 2022**

- fix str processing bug

## 0.2.7

**March 2, 2022**

- add robustness and quality-of-life improvements to data cache
- add 4byte functionality
- add Coingecko functionality

## 0.2.6

**February 24, 2022**

- fix many typing annotation issues
- add Curve functionality
- add Fei functionality

## 0.2.5

**February 16, 2022**

- add ENS functionality
- add hex, ascii, checksum, and lower cli commands
- add Rari lens

## 0.2.4

**February 15, 2022**

- python 3.7 compatibility fixes

## 0.2.3

**February 14, 2022**

- add many cli commands
- refactor existing cli commands

## 0.2.2

**February 11, 2022**

- add python 3.7 and python3.8 compatibility

## 0.2.1

**February 9, 2022**

initial public `ctc` release
