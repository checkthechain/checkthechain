
# Command Line Interface

The `ctc` command line interface can perform many different tasks related to data collection, data analysis, and general block exploration.

Calls to `ctc` follow the general format `ctc <subcommands> [options]`

When using ctc for the first time, run:
    `ctc setup`

To view help about a specific subcommand run:
    `ctc <subcommand> -h`

When `pip` installs the `ctc` python package, it also installs the `ctc` cli program. If your environment does not include installed python scripts in your shell's `PATH`, then you may need to type `python3 -m ctc ...` in the terminal instead of just `ctc ...`.


## Subcommands

All subcommands can be printed typing `ctc help`.

Each cli subcommand has a options to customize its behavior. If you need futher customization, use `ctc` from a python script instead.

```                                                                                  
    cd                     change working directory to specified location            
    config                 print current config information                          
    config edit            edit config values                                        
    config path            print config path                                         
    download-proxy-abi     download proxy abi for contract                           
    setup                  run ctc setup wizard                                      
    rechunk-events         rechunk events by specific chunk size                     
    checksum               compute checksum of address                               
    keccak                 compute keccak hash of data                               
    lower                  convert to lower case                                     
    ascii                  convert hex to ascii                                      
    hex                    convert ascii to hex                                      
    address                summarize address                                         
    block                  summarize block                                           
    blocks                 output information about blocks                           
    call                   output result of a call                                   
    calls                  output the result of multiple calls                       
    eth balance            output ETH balance of address                             
    eth balances           output ETH balance across blocks or addresses             
    erc20 balance          output an ERC20 balance                                   
    erc20 balances         output ERC20 balances across blocks, addresses or tokens  
    erc20 transfers        output information about ERC20 transfers                  
    find                   search for item in directory                              
    gas                    output gas summary of block range                         
    transaction            summarize transaction                                     
    chainlink              output Chainlink feed data                                
    ens                    summarize ENS entry                                       
    ens exists             output whether ENS name exists                            
    ens hash               output hash of ENS name                                   
    ens owner              output owner of ENS name                                  
    ens records            output text records of ENS name                           
    ens resolve            resolve ENS name                                          
    ens reverse            reverse ENS lookup address                                
    fei analytics          output data payload for app.fei.money/analytics           
    fei pcv                output summary of Fei PCV                                 
    fei pcv assets         output summary of Fei PCV assets                          
    fei pcv deposits       output summary of Fei PCV deposits                        
    rari fuse              summarize fuse pool, token, or platform                   
    uniswap mints          output information about pool mints                       
    uniswap burns          output information about pool burns                       
    uniswap swaps          output information about pool mints                       
    uniswap pool           summarize pool                                            
    version                print cli version                                         
    help                   output help
```
