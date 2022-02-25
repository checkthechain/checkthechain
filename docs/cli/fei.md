# FEI CLI Commands
- [`ctc fei pcv`](#ctc-fei-pcv)
- [`ctc fei pcv assets`](#ctc-fei-pcv-assets)
- [`ctc fei pcv deposits`](#ctc-fei-pcv-deposits)
- [`ctc fei analytics`](#ctc-fei-analytics)

## `ctc fei pcv`
output pcv summary statistics

##### Options
- `--block <block-number>`: block number

##### Example Usage:
```bash
> ctc fei pcv
┌─────────────────┐
│ Fei PCV Summary │
└─────────────────┘
                │  amount    
────────────────┼────────────
  total PCV     │  $669.58M  
  total FEI     │  $557.1M   
  user FEI      │  $335.41M  
  protocol FEI  │  $221.69M  
  PCV equity    │  $334.17M  
  CR            │  199.63%
```

## `ctc fei pcv assets`
output table of PCV asset information

##### Options
- `--block <block-number>`: block number

##### Example Usage:
```bash
> ctc fei pcv assets
┌────────────────┐
│ Fei PCV Assets │
└────────────────┘

  asset  │  amount   │  price      │  total     
─────────┼───────────┼─────────────┼────────────
  WETH   │  163.19K  │  $2,628.29  │  $428.90M  
  DAI    │  68.7M    │  $1.00      │  $68.69M   
  RAI    │  6.65M    │  $3.07      │  $20.45M   
  DPI    │  37.89K   │  $152.93    │  $5.79M    
  LUSD   │  94.66M   │  $1.02      │  $96.14M   
  CREAM  │  31.78K   │  $34.51     │  $1.10M    
  agEUR  │  8.83M    │  $1.12      │  $9.89M    
  BAL    │  257.16K  │  $12.08     │  $3.11M
```

## `ctc fei pcv deposits`
output table of PCV deposits

##### Options
- `--block <block-number>`: block number

##### Example Usage:
```bash
> ctc fei pcv deposits
┌──────────────────┐
│ FEI PCV Deposits │
└──────────────────┘
  asset  │  balance   │  name                  │  address                                     
─────────┼────────────┼────────────────────────┼──────────────────────────────────────────────
  WETH   │  $26.28M   │  Tokemak tWETH         │  0x0961d2a545e0c1201b313d14c57023682a546b9d  
  WETH   │  $129.15M  │  Lido stETH            │  0xa271ff86426c7fdaaae72603e6ce68c892d69ed7  
  WETH   │  $43.10M   │  Compound ETH          │  0x0735e14d28ed395048d5fa4a8dbe6e6eb9fc0470  
  WETH   │  $142.71M  │  AAVE ETH              │  0x43ef03755991056681f01ee2182234ef6af1f658  
  WETH   │  $1.15M    │  Uniswap FEI-ETH       │  0x15958381e9e6dc98bd49655e36f524d2203a28bd  
  WETH   │  $23.25K   │  FEI-ETH PSM           │  0x98e5f5706897074a4664dd3a32eb80242d6e694b  
  WETH   │  $6.57M    │  Fuse Pool 146 ETH     │  0xc68412b72e68c30d4e6c0854b439cbbe957146e4  
  WETH   │  $39.42M   │  DAO Timelock ETH      │  0x5e9fa7d783a7f7d4626ce450c8bd2ebbb26dfdb2  
  WETH   │  $40.50M   │  Balancer FEI-WETH     │  0xc5bb8f0253776bec6ff450c2b40f092f7e7f5b57  
  DAI    │  $43.72M   │  Compound DAI          │  0xfde7077aaecdaf2c4b85261aa858c96a7e737a61  
  DAI    │  $19.96M   │  FEI-DAI PSM           │  0x2a188f9eb761f70ecea083ba6c2a40145078dfc2  
  DAI    │  $5.01M    │  Fuse Pool 8 DAI       │  0x9cc46ab5a714f7cd24c59f33c5769039b5872491  
  RAI    │  $10.19M   │  Fuse Pool 9 RAI       │  0xcce230c087f31032fc17621a2cf5e425a0b80c96  
  RAI    │  $10.26M   │  AAVE RAI              │  0x1267b39c93711dd374deab15e0127e4adb259be0  
  RAI    │  $0.00     │  DAO Timelock RAI      │  0x7339ca4ac94020b83a34f5edfa6e0f26986c434b  
  DPI    │  $5.39M    │  DAO Timelock DPI      │  0xb250926e75b1cc6c53e77bb9426baac14ab1e24c  
  DPI    │  $406.38K  │  Fuse Pool 19 DPI      │  0x9a774a1b1208c323eded05e6daf592e6e59caa55  
  LUSD   │  $80.14K   │  Fuse Pool 91 LUSD     │  0x8c51e4532cc745cf3dfec5cebd835d07e7ba1002  
  LUSD   │  $10.17M   │  Fuse Pool 7 LUSD      │  0x6026a1559cdd44a63c5ca9a078cc996a9eb68abb  
  LUSD   │  $80.81M   │  B Protocol LUSD       │  0x374628ebe7ef6aca0574e750b618097531a26ff8  
  LUSD   │  $1.03K    │  FEI-LUSD PSM          │  0xb0e731f036adfdec12da77c15aab0f90e8e45a0e  
  LUSD   │  $5.08M    │  Fuse Pool 8 LUSD      │  0xf846ee6e8ee9a6fbf51c7c65105cabc041c048ad  
  CREAM  │  $1.10M    │  CREAM Hack Repayment  │  0x3a1838ac9eca864054bebb82c32455dd7d7fc89c  
  agEUR  │  $9.89M    │  Uniswap FEI-agEUR     │  0x7ac2ab8143634419c5bc230a9f9955c3e29f64ef  
  agEUR  │  $0.00     │  DAO Timelock agEUR    │  0x485d23ce5725ecde46ca9033012984d90b514ffd  
  BAL    │  $3.11M    │  Balancer BAL-WETH     │  0xcd1ac0014e2ebd972f40f24df1694e6f528b2fd4  

┌─────────────────┐
│ FEI Deployments │
└─────────────────┘
  asset  │  balance   │  name                │  address                                     
─────────┼────────────┼──────────────────────┼──────────────────────────────────────────────
  FEI    │  $64.19M   │  OA Account          │  0x7eb88140af813294aedce981b6ac08fcd139d408  
  FEI    │  $20.62M   │  Fuse Pool 8         │  0xd6598a23418c7fef7c0dc863265515b623b720f9  
  FEI    │  $282.56K  │  Fuse Pool 90 FEI    │  0xec54148cbc47bff8fcc5e04e5e8083adb8af9ad9  
  FEI    │  $2.54M    │  Fuse Pool 79 FEI    │  0xb3a026b830796e43bfc8b135553a7573538ab341  
  FEI    │  $3.16M    │  Fuse Pool 6         │  0x7aa4b1558c3e219cfffd6a356421c071f71966e7  
  FEI    │  $600.15K  │  Fuse Pool 19        │  0x7e39bba9d0d967ee55524fae9e54900b02d9889a  
  FEI    │  $452.08K  │  Fuse Pool 24        │  0x508f6fbd78b6569c29e9d75986a51558de9e5865  
  FEI    │  $50.00K   │  Fuse Pool 25        │  0xb4ffd10c4c290dc13e8e30bf186f1509001515fd  
  FEI    │  $128.51K  │  Balancer FEI-TRIBE  │  0x89dfbc12001b41985efabd7dfcae6a77b22e4ec3  
  FEI    │  $1.04M    │  Fuse Pool 27        │  0xe2e35097638f0ff2eeca2ef70f352be37431945f  
  FEI    │  $803.89K  │  Fuse Pool 18        │  0x07f2dd7e6a78d96c08d0a8212f4097dcc129d629  
  FEI    │  $50.00K   │  Fuse Pool 31        │  0x05e2e93cfb0b53d36a3151ee727bb581d4b918ce  
  FEI    │  $16.32M   │  Aave V2 FEI Pool    │  0xfac571b6054619053ac311da8112939c9a374a85  
  FEI    │  $1.00M    │  Fuse Pool 127 FEI   │  0xa62ddde8f799873e6fcdbb3acbba75da85d9dcde  
  FEI    │  $150.34K  │  Fuse Pool 22 FEI    │  0xa2bdbcb95d31c85bae6f0fa42d55f65d609d94ee  
  FEI    │  $150.05K  │  Fuse Pool 72 FEI    │  0x395b1bc1800fa0ad48ae3876e66d4c10d297650c  
```

## `ctc fei analytics`
- generate data payload for [app.fei.money/analytics](https://app.fei.money/analytics)

##### Options
- `timescale`: time window and time precision of data samples
- `--path`: file path to write json blob
- `--overwrite`: overwrite output path if file already exists

##### Example Usage:
```bash
> ctc fei analytics 30d, 1d

[outputs large json blob]
```
