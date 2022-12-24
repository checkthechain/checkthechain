
## How to upgrade to new `ctc` version
- update the `__version__` attribute in ctc's root `__init__.py`
- in `ctc.config.upgrade_utils.data_dir_versioning`:
    - add new version to `data_spec_order`
    - add file layout to `data_dir_specs`
