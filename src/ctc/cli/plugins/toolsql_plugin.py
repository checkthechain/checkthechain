from __future__ import annotations

import typing

import toolcli


command_index: toolcli.CommandIndex = {
    # ('db', 'config'): 'toolsql.cli.commands.sql.config_command',
    ('db', 'login'): 'toolsql.cli.commands.sql.login_command',
    # ('db', 'schema'): 'toolsql.cli.commands.sql.schema_command',
    # ('db', 'usage'): 'toolsql.cli.commands.sql.usage_command',
    # ('db', 'migrate', 'all'): 'toolsql.cli.commands.sql.migrate.all_command',
    # (
    #     'db',
    #     'migrate',
    #     'apply',
    # ): 'toolsql.cli.commands.sql.migrate.apply_command',
    # (
    #     'db',
    #     'migrate',
    #     'create',
    # ): 'toolsql.cli.commands.sql.migrate.create_command',
    # ('db', 'migrate', 'edit'): 'toolsql.cli.commands.sql.migrate.edit_command',
    # (
    #     'db',
    #     'migrate',
    #     'purge',
    # ): 'toolsql.cli.commands.sql.migrate.purge_command',
    # ('db', 'migrate', 'root'): 'toolsql.cli.commands.sql.migrate.root_command',
    # (
    #     'db',
    #     'migrate',
    #     'setup',
    # ): 'toolsql.cli.commands.sql.migrate.setup_command',
    # (
    #     'db',
    #     'migrate',
    #     'status',
    # ): 'toolsql.cli.commands.sql.migrate.status_command',
}


required_extra_data: typing.Sequence[str] = ['db_config', 'db_schema']


plugin: toolcli.Plugin = {
    'command_index': command_index,
    'required_extra_data': required_extra_data,
    'help_category': 'admin',
}
