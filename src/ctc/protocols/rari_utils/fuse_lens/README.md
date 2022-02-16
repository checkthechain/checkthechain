
# Rari Fuse Lens

This is an almost 1:1 wrapper of the Rari Fuse lens contracts in python

Differences from the lens contracts deployed on-chain:
- Some on-chain lens functions cause Geth to revert due to gas limits. These functions have been reimplemented in python here so that they can be used without reverts. These functions:
    - `getPublicPoolsWithData`
    - `getPublicPoolsByVerificationData`
    - `getPublicPoolUsersWithData`
- One of the two `getPoolUsersWithData` functions has been renamed to `getPoolsUsersWithData` to prevent name collision.
- A default value of `1e36` is used for all functions that take a `maxHealth` argument, so that all users are returned by default.
- Functions return dicts instead of lists for readability, and some of the redundant "list of indexes" return arguments have been omitted.
- Snake case is used instead of camel case for pythonicity.


## Example Usage

```python
from ctc.protocols.rari_utils import fuse_lens

result = await fuse_lens.async_get_public_pool_users_with_data()
```


## Resources
- Rari Fuse lens docs https://docs.rari.capital/fuse/#fuse-pool-lens
- primary Fuse lens abi https://github.com/Rari-Capital/RariSDK/blob/master/src/Fuse/contracts/abi/FusePoolLens.json
- secondary Fuse lens abi https://github.com/Rari-Capital/RariSDK/blob/master/src/Fuse/contracts/abi/FusePoolLensSecondary.json

