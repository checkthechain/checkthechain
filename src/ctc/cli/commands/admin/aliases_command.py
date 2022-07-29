from __future__ import annotations

import toolcli

from ctc.cli.cli_utils import cli_alias_utils


aliases_help = """these aliases allow you to call ctc subcommands without typing the "ctc" part

    for example, you can type [option]4byte 0xa9059cbb[/option] instead of [option]ctc 4byte 0xa9059cbb[/option]

these aliases must go in your shell config file

    this can be done using one of the following methods:
    1. use [option]ctc aliases --append[/option] to append to autodetected config files
    2. use [option]ctc aliases >> CONFIG_PATH[/option] to append the aliases to config file
    3. manually paste the aliases into your config file

    the path to your terminal file depends on shell:
    - bash: [metavar]~/.profile[/metavar] or [metavar]~/.bashrc[/metavar]
    - zsh: [metavar]~/.zshrc[/metavar]
    - fish: [metavar]~/.config/fish/config.fish[/metavar]

to learn more about the underlying commands, run [option]ctc help[/option]

depending on preference, can use all aliases or just a subset of them"""


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': aliases_command,
        'help': 'view and manage ctc shell aliases' + '\n\n' + aliases_help,
        'args': [
            {
                'name': '--raw',
                'help': 'output aliases as raw script file',
                'action': 'store_true',
            },
            {
                'name': '--install',
                'help': 'install/upgrade aliases in shell config (will ask for confirmation)',
                'action': 'store_true',
            },
        ],
        'examples': {
            '': {},
            '--raw': {},
            '--install': {'runnable': False},
        },
    }


def aliases_command(*, raw: bool, install: bool) -> None:

    if raw:
        cli_alias_utils.print_raw_aliases()
    elif install:
        cli_alias_utils.install_aliases()
    else:
        cli_alias_utils.print_alias_status()
