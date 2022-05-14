
- db_crud: low level functions for interacting with db
- db_intake: high level functions for writing to db
- db_queries: high level functions for reading from db
- db_spec: schema definitions and custom types


## Connections
- db_crud functions require a connection to be provided in their inputs
- db_intake and db_queries create their own connections
