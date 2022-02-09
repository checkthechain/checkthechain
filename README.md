# ⛓🔍 Check the Chain (`ctc`) 🔎⛓

`ctc` is a cli tool and python library for historical data analysis of Ethereum and other EVM chains

###### *`ctc` is in beta, please report bugs to the issue tracker*


## Features
- **data collection**: uses highly optimized data fetching for data aggregation from archive nodes
- **data storage**: stores collected data on disk so that it only needs to be collected once
- **data analysis**: computes derived metrics and other quantitative data summaries
- **data visualization**: plots data to maximize data interpretability and sharing
- **protocol specific**: includes functionality for protocols like Chainlink, Uniswap, ERC20's, DAO Governors, and more
- **command line interface**: performs many block explorer tasks even if you're not a python user

for details check out [the docs](/docs)

## Why does `ctc` exist?
- **Treat historical data as a first-class feature**: This means having historical data features well-integrated into each part of the of the API.
- **Clean api that emphasizes UX**: With `ctc` most data queries can be obtained with a single function call. No need to instantiate objects. RPC inputs/outputs are automatically encoded/decoded by default.


## Contents
1. [Example Usage](#example-usage)
2. [Installation](#installation)
3. [Related Projects](#related-projects)


## Example Usage

for complete list of examples see [examples](/docs/examples) in the docs


#### Get all token transfers of an ERC20

```python
from ctc import evm

# get token transfers
transfers = await evm.async_get_erc20_transfers(
    token_address='0x956f47f50a910163d8bf957cf5846d573e7f87ca',
    event_name='Transfer',
)

# get holdings of each address for a given block
holdings = evm.get_erc20_holdings_from_transfers(transfers=transfers, block=12345789)
```


#### Get swaps, mints, and burns for a Uniswap pair

```python
from ctc.protocols import uniswap_v2_utils

pool_address = '0x94b0a3d511b6ecdb17ebf877278ab030acb0a878'

swaps = await uniswap_v2_utils.async_get_pool_swaps(pool_address)
mints = await uniswap_v2_utils.async_get_pool_mints(pool_address)
burns = await uniswap_v2_utils.async_get_pool_burns(pool_address)
```


#### Get historical data for a Chainlink feed
```python
from ctc.protocols import chainlink_utils

feed_address = '0x31e0a88fecb6ec0a411dbe0e9e76391498296ee9'

feed_data = await chainlink_utils.async_get_feed_data(feed_address)
```


#### Get DAO proposals and votes

```python
from ctc import evm

dao_address = '0x0bef27feb58e857046d630b2c03dfb7bae567494'

proposal_events = await evm.async_get_events(
    contract_address=dao_address,
    event_name='ProposalCreated',
)

vote_events = await evm.async_get_events(
    contract_address=dao_address,
    event_name='VoteCast',
)
```


## Installation

Two steps:
1. `pip install checkthechain`
2. run `ctc setup` command in terminal to specify data provider and data storage path

If your shell's `PATH` does not include python scripts you may need to do something like `python3 -m pip ...` and `python3 -m ctc ...`


## Related Projects
- [`ethereum-etl`](https://github.com/blockchain-etl/ethereum-etl) ETL tools for bulk data gathering in python
- [`seth`](https://github.com/dapphub/dapptools/tree/master/src/seth) swiss army knife cli tool for Ethereum
- [`web3.py`](https://github.com/ethereum/web3.py/) official Ethereum python client
- [`gnosis-py`](https://github.com/gnosis/gnosis-py) python tools for Ethereum and Gnosis projects
- [`eth-abi`](https://github.com/sslivkoff/eth-abi-lite) python library for encoding/decoding EVM data
- [`eth-utils`](https://github.com/ethereum/eth-utils) general python libraries for interacting with Ethereum
- [`brownie`](https://github.com/eth-brownie/brownie) SDK for EVM smart contract development
- [`riemann-ether`](https://github.com/summa-tx/riemann-ether) ethereum rapid prototyping toolbox
