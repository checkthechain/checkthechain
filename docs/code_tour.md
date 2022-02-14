
# Codebase Tour

This is the general layout of the `ctc` codebase.


## `ctc` Subpackages

- `ctc.binary`: utilities for hashing and abi encoding/decoding
- `ctc.cli`: ctc command line implementation
- `ctc.config`: config loading and management
- `ctc.directory`: token and contract addresses as well as chain_id's 
- `ctc.evm`: high-level functions for EVM standards and objects
- `ctc.protocols`: subpackages for working with specific protocols like Uniswap or Chainlink
- `ctc.rpc`: utilities for communicating over rpc
- `ctc.spec`: types, typeguards, and abstract specifications
- `ctc.toolbox`: miscellaneous python utilities


## Code Conventions


#### Typing

`ctc` uses python type hinting features for static analysis of the codebase. This helps catch many errors before they can appear at runtime. Checks are currently performed using `mypy=0.930`. Custom types used by `ctc` can be found in the `ctc.spec` subpackage.


#### Async

`ctc` uses `async` for functions that make network calls or database calls. This allows high levels of concurrency and increases the overall speed of historical data aggregation.

To use `async` functions they must be run from an event loop. These functions can be called from synchronous code as follows:

```python
import asyncio


result = asyncio.run(some_async_function(input1, input2))
```

If you are using IPython or Jupyter notebooks, you can directly `await` the `async` functions without using `asyncio.run()`:


```python

result = await some_async_function(input1, input2)
```

If you open up network connections you should also close them at the end of your scipt, for example:

```python
from ctc import rpc

await rpc.async_close_http_session(provider=provider)
```

*Future Roadmap*: will create wrappers to make calling `async` code from synchronous code more ergonomic


## Dependencies

`ctc` requires `python3.7` through `python3.10` and depends on a few different types of external packages:

1. **data science dependencies** include standard python library packages including `numpy`, `matplotlib`, and `pandas`.
2. **IO dependencies** include data formatting 
3. **toolsuite dependencies** are general python utilities coming the `toolsuite` set of repos. These are written by the same authors as `ctc`.
4. **EVM/Cryptography dependencies** include `pycryptodome`, `rlp`, and `eth_abi`.

Note also that each of these dependencies has its own dependencies.

Dependence on these packages will be minimized in future releases to minimize attack surface and to maximize the number of environments in which `ctc` can be run. Some of the common libraries in the EVM ecosystem have incompatible requirements. For example, `ethereum-etl` requires older versions of `web3py` and `eth_abi`, and so a single environment cannot contain the most recent versions of all of these packages. `ctc` aims to avoid these types of compatibility problems by minimizing dependencies.

