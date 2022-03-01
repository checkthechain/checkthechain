# 4byte

4byte is a database of function signatures and event signatures

4byte allows for getting the human readable form of a function or event signature from its hashed representation

`ctc.protocols.fourbyte_utils` Features
- works for both function signatures and event signatures
- allows queries to either `www.4byte.directory` or queries to a local copy

## Usage Examples

##### Build Local Copy of 4byte Database

```python
from ctc.protocols import fourbyte_utils

await fourbyte_utils.async_build_function_signatures_dataset()
await fourbyte_utils.async_build_event_signatures_dataset()
```

##### Query Function Signature

```python
from ctc.protocols import fourbyte_utils

# these returns the same results
results = fourbyte_utils.query_function_signature('0x4554e008')
results = fourbyte_utils.query_function_signature(text_signature='withdrawAndMigrate()')
```

## CLI Commands

For 4byte ctc cli commands see [/docs/cli/protocols/4byte.md](4byte cli docs)

