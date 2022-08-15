
## Checklist for adding new db schemas
- create definition files in `ctc.db.schemas.<schema_name>`:
    - `<schema_name>_intake.py`: streamlined db population functions
    - `<schema_name>_queries.py`: high-level queries
    - `<schema_name>_schema_defs.py`: table definitions
    - `<schema_name>_statements.py`: low level SELECT/INSERT/DELETE statements
- add `<schema_name>` to schema_utils:
    - add to either `GenericSchemaName` or `NetworkSchemaName`
    - add to `get_raw_schema()`
- add `<schema_name>` to `db.management.active_utils.get_active_schemas()`
- add `<schema_name>` to `config.config_data_sources.get_data_source()`
- add schema tests
    - cookiecutter tests in `tests/ctc/db/test_crud_probems.py`
    - additional tests in `tests/ctc/db/db_crud/test_db_<schema_name>.py`

*TODO*: drastically simplify the schema addition process
