# ⛓🔍 Check the Chain (`ctc`) 🔎⛓

`ctc` is a tool for historical data analysis of Ethereum and other EVM chains

It can be used as either 1) a python package or 2) a cli tool

###### *`ctc` is in beta, please report bugs to the issue tracker*


## Features
- **data collection**: collects data from archive nodes robustly and efficiently
- **data storage**: stores collected data on disk so that it only needs to be collected once
- **data coding**: handles data encoding and decoding automatically by default
- **data analysis**: computes derived metrics and other quantitative data summaries
- **data visualization**: plots data to maximize data interpretability and sharing
- **protocol specificity**: includes functionality for protocols like Chainlink, Uniswap, ERC20, and more
- **command line interface**: performs many block explorer tasks in the terminal

for details check out [the docs](/docs)


## Contents
1. [**Example Usage**](#example-usage)
    1. [**ERC20**: get all token transfers and balances of an ERC20](#get-all-token-transfers-of-an-erc20)
    2. [**Uniswap**: get swaps, mints, and burns of a Uniswap pair](#get-swaps-mints-and-burns-for-a-uniswap-pair)
    3. [**Chainlink**: get historical data for a Chainlink feed](#get-historical-data-for-a-chainlink-feed)
    4. [**DAO**: get DAO proposals and votes](#get-dao-proposals-and-votes)
2. [**Installation**](#installation)
3. [**FAQ**](#faq)
4. [**Related Projects**](#related-projects)


## Example Usage

for more examples see [the examples](/docs/examples) in the docs


#### Get all token transfers of an ERC20

```python
# python

from ctc import evm

# get token transfers
transfers = await evm.async_get_erc20_transfers(
    token_address='0x956f47f50a910163d8bf957cf5846d573e7f87ca',
    event_name='Transfer',
)

# get holdings of each address for a given block
holdings = evm.async_get_erc20_holdings_from_transfers(transfers=transfers, block=12345789)
```

```bash
# bash

ctc erc20 transfers 0x956f47f50a910163d8bf957cf5846d573e7f87ca \
    --output transfers.csv

ctc erc20 balances 0x956f47f50a910163d8bf957cf5846d573e7f87ca \
    --output balances.csv \
    --block 12345789
```

#### Get DAO proposals and votes

```python
# python

from ctc import evm

dao_address = '0x0bef27feb58e857046d630b2c03dfb7bae567494'

proposals = await evm.async_get_events(
    contract_address=dao_address,
    event_name='ProposalCreated',
)

votes = await evm.async_get_events(
    contract_address=dao_address,
    event_name='VoteCast',
)
```

```bash
# bash

DAO="0x0bef27feb58e857046d630b2c03dfb7bae567494"

ctc events 0x31e0a88fecb6ec0a411dbe0e9e76391498296ee9 ProposalCreated --output proposals.csv
ctc events 0x31e0a88fecb6ec0a411dbe0e9e76391498296ee9 VoteCast --output votes.csv
```

#### Get historical data for a Chainlink feed
```python
# python

from ctc.protocols import chainlink_utils

feed = '0x31e0a88fecb6ec0a411dbe0e9e76391498296ee9'

data = await chainlink_utils.async_get_feed_data(feed)
```

```bash
# bash

ctc chainlink 0x31e0a88fecb6ec0a411dbe0e9e76391498296ee9 --output data.csv
```

#### Get swaps, mints, and burns of a Uniswap pool

```python
# python

from ctc.protocols import uniswap_v2_utils

pool = '0x94b0a3d511b6ecdb17ebf877278ab030acb0a878'

swaps = await uniswap_v2_utils.async_get_pool_swaps(pool)
mints = await uniswap_v2_utils.async_get_pool_mints(pool)
burns = await uniswap_v2_utils.async_get_pool_burns(pool)
```

```bash
# bash

POOL="0x94b0a3d511b6ecdb17ebf877278ab030acb0a878"

ctc uniswap swaps $POOL --output swaps.csv
ctc uniswap mints $POOL --output mints.csv
ctc uniswap burns $POOL --output burns.csv
```


## Installation

Two steps:
1. `pip install checkthechain`
2. run `ctc setup` in terminal to specify data provider and data storage path

If your shell's `PATH` does not include python scripts you may need to do something like `python3 -m pip ...` and `python3 -m ctc ...`


## FAQ
- What are the goals of `ctc`?
    - **Treat historical data as a first-class feature**: This means having historical data functionality well-integrated into each part of the of the API. It also means optimizing the codebase with historical data workloads in mind.
    - **Clean API emphasizing UX**: With `ctc` most data queries can be obtained with a single function call. No need to instantiate objects. RPC inputs/outputs are automatically encoded/decoded by default.
    - **Maximize data accessibility**: Blockchains contain vast amounts of data, but accessing this data can require large amounts of time, effort, and expertise. `ctc` aims to lower the barrier to entry on all fronts.
- Why use `async`?
    - `async` is a natural fit for efficiently querying large amounts of data from an archive node. All `ctc` functions that fetch external data use `async`. For tips on using `async` see [this section](/docs/code_tour.md#async) in the docs. Future versions of `ctc` will include some wrappers for synchronous code.
- Do I need an archive node?
    - If you want to query historical data, you will need an archive node. You can either [run one yourself](https://github.com/ledgerwatch/erigon) or use a third-party provider such as [Alchemy](https://www.alchemy.com/) or [Quicknode](https://www.quicknode.com/). You can also use `ctc` to query current (non-historical) data using a non-archive node.


## Related Projects
- [`ethereum-etl`](https://github.com/blockchain-etl/ethereum-etl) ETL tools for bulk data gathering in python
- [`pycryptodome`](https://github.com/Legrandin/pycryptodome) self-contained cryptographic library for python
- [`web3.py`](https://github.com/ethereum/web3.py/) official Ethereum python client
- [`eth-abi`](https://github.com/sslivkoff/eth-abi-lite) python library for encoding/decoding EVM data

