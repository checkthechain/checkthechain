# ⛓🔍 Check the Chain (`ctc`) 🔎⛓

`ctc` is a tool for collecting and analyzing data from Ethereum and other EVM chains

It can be used as either 1) a python package or 2) a cli tool

###### *`ctc` is in beta, please report bugs to the issue tracker*


## Features
- **data collection**: collects data from archive nodes robustly and efficiently
- **data storage**: stores collected data on disk so that it only needs to be collected once
- **data coding**: handles data encoding and decoding automatically by default
- **data analysis**: computes derived metrics and other quantitative data summaries
- **data visualization**: plots data to maximize data interpretability
- **protocol specificity**: includes functionality for protocols like Chainlink, Uniswap, ERC20, and more
- **command line interface**: performs many block explorer tasks in the terminal

For detailed information check out [the documentation](https://ctc.readthedocs.io/)


## Contents
1. [**Example Usage**](#example-usage)
    1. [**ERC20**: get all token transfers and balances of an ERC20](#get-all-token-transfers-of-an-erc20)
    2. [**Uniswap**: get swaps, mints, and burns of a Uniswap pair](#get-swaps-mints-and-burns-for-a-uniswap-pair)
    3. [**Chainlink**: get historical data for a Chainlink feed](#get-historical-data-for-a-chainlink-feed)
    4. [**DAO**: get DAO proposals and votes](#get-dao-proposals-and-votes)
2. [**Installation**](#installation)
3. [**FAQ**](#faq)
4. [**Similar Projects**](#similar-projects)

<table>
  <tbody>
    <tr>
      <td>
        <b>📜 Legal Disclaimer 📜</b> As stated in the MIT license, <code>ctc</code> comes with no warranty of any kind. The authors of <code>ctc</code> accept no responsibility for any damages or negative outcomes that result from using <code>ctc</code> or <code>ctc</code>-derived data. <code>ctc</code> is not audited and using it as a basis for making financial decisions is not recommended.
      </td>
    </tr>
  </tbody>
</table>

## Example Usage

for more examples see examples in [the docs](https://ctc.readthedocs.io/en/latest/index.html#datatypes)


#### Get all token transfers of an ERC20

```python
# python

from ctc import evm

# get token transfers
transfers = await evm.async_get_erc20_transfers(
    token='0x956f47f50a910163d8bf957cf5846d573e7f87ca',
    event_name='Transfer',
)

# get holdings of each address for a given block
holdings = await evm.async_get_erc20_balances_from_transfers(transfers=transfers, block=12345789)
```

```bash
# bash

ctc erc20 transfers 0x956f47f50a910163d8bf957cf5846d573e7f87ca \
    --export transfers.csv

ctc erc20 balances 0x956f47f50a910163d8bf957cf5846d573e7f87ca \
    --export balances.csv \
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
    include_timestamps=True,
)
```

```bash
# bash

DAO="0x0bef27feb58e857046d630b2c03dfb7bae567494"

ctc events $DAO ProposalCreated --export proposals.csv
ctc events $DAO VoteCast --export votes.csv
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

ctc chainlink 0x31e0a88fecb6ec0a411dbe0e9e76391498296ee9 --export data.csv
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

ctc uniswap swaps $POOL --export swaps.csv
ctc uniswap mints $POOL --export mints.csv
ctc uniswap burns $POOL --export burns.csv
```


## Installation

Two steps:
1. `pip install checkthechain`
2. run `ctc setup` in terminal to specify data provider and data storage path

If your shell's `PATH` does not include python scripts you may need to do something like `python3 -m pip ...` and `python3 -m ctc ...`

Detailed instructions can be found in the [installation documentation](https://ctc.readthedocs.io/en/latest/overview/installation.html).

`ctc` requires python >= 3.7. 

## FAQ
- What are the goals of `ctc`?
    1. **Treat historical data as a first-class feature**: This means having historical data functionality well-integrated into each part of the of the API. It also means optimizing the codebase with historical data workloads in mind.
    2. **Protocol-specific functionality**: This means having built-in support for popular on-chain protocols.
    3. **Terminal-based block explorer**: This means supporting as many block explorer tasks as possible from the terminal. And doing so in a way that is faster than can be done with a web browser.
    4. **Clean API emphasizing UX**: With `ctc` most data queries can be obtained with a single function call. No need to instantiate objects. RPC inputs/outputs are automatically encoded/decoded by default.
    5. **Maximize data accessibility**: Blockchains contain vast amounts of data, but accessing this data can require large amounts of time, effort, and expertise. `ctc` aims to lower the barrier to entry on all fronts.
- Why use `async`?
    - `async` is a natural fit for efficiently querying large amounts of data from an archive node. All `ctc` functions that fetch external data use `async`. For tips on using `async` see [this section](https://ctc.readthedocs.io/en/latest/python/async_code.html) in the docs. Future versions of `ctc` will include some wrappers for synchronous code.
- Do I need an archive node?
    - If you want to query historical data, you will need an archive node. You can either [run one yourself](https://github.com/ledgerwatch/erigon) or use a third-party provider such as [Alchemy](https://www.alchemy.com/), [Quicknode](https://www.quicknode.com/), or [Moralis](https://moralis.io/speedy-nodes/). You can also use `ctc` to query current (non-historical) data using a non-archive node.
- Is `ctc` useful for recent, non-historical data?
    - Yes, `ctc` has lots of functionality for querying the current state of the chain.


## Similar Projects
- [`ethereum-etl`](https://github.com/blockchain-etl/ethereum-etl) ETL tools for bulk data gathering in python
- [`Trueblocks`](https://github.com/TrueBlocks/trueblocks-core) optimized EVM local indexing engine
- [`cast`](https://onbjerg.github.io/foundry-book/reference/cast.html) cli EVM swiss army knife (rust)
- [`seth`](https://github.com/dapphub/dapptools/tree/master/src/seth) cli EVM swiss army knife (bash / js)
- [`ethereal`](https://github.com/wealdtech/ethereal) cli EVM swiss army knife (go)
- [`web3.py`](https://github.com/ethereum/web3.py/) official Ethereum python client
- [`ape`](https://github.com/ApeWorX/ape) general python framework for many tasks including smart contract dev
- [`ethtx.info`](https://ethtx.info/) EVM transaction trace visualizer

