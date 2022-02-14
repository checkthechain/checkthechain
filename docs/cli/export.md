# `ctc export`

The `ctc export` cli command can export a variety of data types into a variety of formats

Export calls follow the template `ctc export <export_type> [options]`


## Contents
- [Export Types](#export-types)
- [Export Options](#export-options)


## Export Types

There are three main types of exports:
- `Metric Exports`: exported over any arbitrary list of blocks
    - derived mostly from blockwise rpc methods
    - example: oracle prices
- `Event Exports`: exported over a range of blocks
    - derived mostly from events
    - example: individual DEX trades
- `Snapshot Exports`: exports multiple datapoints within a single block
    - example: ERC20 holdings of multiple wallets

#### Metric Export Types
- `events {<event_hash> | <event_name>} [<topic_name>=<topic_value]*`
- `erc20 transfers {<token_address> | <token_symbol>}`
- `uniswap {swaps | mints | burns} {<pool_address>}`

#### Event Export Types
- `calls {<call_data> | (<function_name> [<function_parameters>]})`
- `eth <address>`
- `blocks [<block_attribute>]`
- `erc20 {supply | balance | allowance} {<token_address> | <token_symbol>} [<address>]`
- `chainlink {<feed_address> | <feed_name>}`
- `uniswap {price | volume | depth} {<pool_address>}`

#### Snapshot Export Types
- `erc20 holders {<token_address> | <token_symbol>} [<addresses>]`


## Export Options

these are additional options that can be applied to various exports

#### Provider Options
- `--network`: name or id of network

#### Metric Export Options
- `--blocks`: comma-separated list of blocks
- `--start-block`: initial block for data range
- `--end-block`: final block for data range
- `--block-interval`: interval of block sampling range

#### Event Export Options
- `--start-block`: initial block for data range
- `--end-block`: final block for data range

#### Snapshot Export Options
- `--block`: block to use for snapshot

#### Output Options
- `--output <filepath>`: output to a file instead of stdout, should be csv or json
- `--overwrite`: allows output file to be overwitten if it already exists

