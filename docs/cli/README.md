
# Command Line Interface

The `ctc` command line interface can perform many different tasks related to data collection, data analysis, and general block exploration.

Calls to `ctc` follow the general format `ctc <subcommands> [options]`.

When `pip` installs the `ctc` python package, it also installs the `ctc` cli program. If your environment does not include installed python scripts in your shell's `PATH`, then you may need to type `python3 -m ctc ...` in the terminal instead of just `ctc ...`.


## Subcommands

All subcommands can be printed typing `ctc` with no arguments.

Each cli subcommand has a variety of options to customize its output. If you need more customization than these options provide, then you should use `ctc` from a python script instead.

```
    cd                  change working directory to a ctc directory
    config              print current ctc config
    config edit         edit current ctc config
    config path         print current ctc config path
    download-proxy-abi  download a proxy implementation of an abi
    setup               run ctc setup wizard
    rechunk-events      rechunk how events are stored on disk
    keccak              compute keccak hash of a hex or text string
    address             print summary of an address, includin abi
    block               print summmary of a block
    blocks              export block data
    call                print output of a contract call
    calls               export calls across contracts or blocks
    eth balance         print eth balance of a single wallet
    eth balances        export eth balances across wallets or blocks
    erc20 balance       print an erc20 balance of a single wallet
    erc20 balances      export balances of erc20s, blocks, or addresses
    erc20 transfers     export transfers of an erc20
    events              export events
    gas                 export gas pricing statistics
    transaction         print summary of a transaction
    chainlink           export chainlink feed data
    fei payload         export fei collateralization data
    rari fuse           export rari
    uniswap mints       export mints of a uniswap pool
    uniswap burns       export burns of a uniswap pool
    uniswap swaps       export swaps of a uniswap pool
    uniswap pool        print summary of a uniswap pool
```

Better examples of each command coming soon

