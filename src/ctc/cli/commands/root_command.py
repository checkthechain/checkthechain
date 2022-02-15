# from ctc.cli import cli_run


def get_command_spec():
    return {
        'f': root_command,
    }


available_subcommands = """
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
    uniswap pool        print summary of a uniswap pool"""


def root_command():
    print('check the chain')
    print()
    print('usage:')
    print('    ctc <subcommands> [options]')
    print()
    print('available subcommands:')
    # for command in cli_run.command_index.keys():
    #     if command == ():
    #         continue
    #     print('   ', ' '.join(command))
    print()
    print(available_subcommands)

