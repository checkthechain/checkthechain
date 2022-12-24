
## How to add a new key to config
- **Types**: Add new key to each of the config types in `ctc.spec.typedefs.config_types`
- **JSON Conversion**: If new key uses maps that use integers as subkeys, specify appropriate type conversions:
    - If these are only top-level keys, can add to `ctc.spec.typedata.config_int_subkeys`
    - Otherwise can add conversion to `ctc.config.config_read.get_config()`
- **Defaults**: Add default values for key to `ctc.config.config_defaults.get_default_config()`
- **Getters**: Add appropriate getter functions to `ctc.config.config_values`
- **Validation**: Add necessary validation funcitons to `ctc.config.config_validate.get_config_validators()` and add base types to `ctc.config.config_validate.get_config_base_types()`
- **Versioning**: Increase ctc version (see guide on "How to upgrade ctc version")
- **Upgrades**: Create new config version upgrade function in `ctc.config.upgrade_utils`
    - Include new key in upgrade function
    - Add new upgrade function to `ctc.config.upgrade_utils.config_upgrade.get_config_upgrade_functions()`
    - Add new `LegacyConfig__X_Y_Z` class to `ctc.config.upgrade_utisl.legacy_types`

