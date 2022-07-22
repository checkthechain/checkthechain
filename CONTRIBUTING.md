
# Tests

PR's should pass all tests before merging. Non-trivial code contributions should also add new tests to the test suite to verify that the code works as intended. Such tests also prevent the contribution from silently breaking in the future.

Mypy is used for type annotation testing. Pytest is used for writing tests. Tox is used for running tests across multiple types of python environments.

Relevant testing commands:
- Run `mypy` in the root directory to test type annotations
- Run `pytest` in the root directory to run tests with whatever python environment is currently active
- Run `tox` in the root directory to run tests against a variety of python environments

The `pyproject.toml` file in the root directory contains the configuration for each of these tools.

Useful arguments when running the tests:
- `pytest -n 20` will run the tests in 20 parallel threads, which will greatly speed up the total time needed for testing.
- `pytest --lf` will rerun only those tests that failed in the previous testing run, which is helpful for efficiently debugging a failing test.
- `pytest --pdb` will drop into an interactive debugger each time a test fails.

Running the tests will require an archive node RPC provider. Free third-party providers might have ratelimits that are too low to be able to run the tests in a reasonable amount of time.


## Development

If you run into errors when running cli commands, can use the `--debug` argument to drop into a debugger at the point of failure.


# Coding Conventions

These are strong suggestions rather than strict rules

## Typing Annotations
- use mypy
- use strict mode
- avoid using `typing.Any` or `typing.cast()` whenever possible
- when using general functions that return `Any`, like `json.load()` or `rpc.async_batch_execute()`:
    - validate simple datatypes
    - avoid validating `TypedDict` entries for now
        - wait until a good solution is created either in the python standard library or a 3rd party library
- until mypy has a mature implementation of variadic generics, use:
    - `spec.NumpyArray` for numpy arrays
    - `spec.Series` for pandas Series
    - `spec.DataFrame` for pandas DataFrames


## API guide
- naming conventions
    - use consistent variable names across related functions
    - only use by_block, dont use by_blocks or per_block
- argument design
    - if there is one main argument, don't require a keyword for that argument
    - if there are multiple mutually exclusive arguments, and those arguments can robustly be distinguished by types, can use a single positional argument as first argument instead of breaking them up into keyword arguments
    - keyword only arguments
        - typically use keyword-only arguments when any of the following apply:
            - using optional arguments
            - using lots of arguments
            - using non-obvious or difficult-to-remember arguments
        - typically avoid keyword only arguments when any of the following apply:
            - function has an obvious core set of arguments
            - arguments can be distinguished by type, allowing for generic positionals
        - advantages:
            - more explicit
            - safer
            - more maintainable
- async functions should have a name that starts with `async_`
