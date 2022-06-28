from __future__ import annotations

import typing

import toolcli

from ctc.cli.cli_utils import cli_alias_utils


def add_cli_aliases(styles: typing.Mapping[str, str]) -> None:

    print()
    print()
    toolcli.print('## Installing CLI Aliases', style=styles['header'])

    alias_status = cli_alias_utils.get_alias_status()

    if len(alias_status['no_aliases']) == 0:
        print()
        cli_alias_utils.print_alias_status(alias_status=alias_status, styles=styles)
    else:
        print()
        print(
            'ctc can install cli aliases to make many commands quicker to type'
        )
        print()
        toolcli.print(
            'For example, you cna type '
            + toolcli.add_style('4byte 0xa9059cbb', styles['command'])
            + ' instead of '
            + toolcli.add_style('ctc 4byte 0xa9059cbb', styles['command'])
        )
        print()
        print('ctc has aliases prepared for the following commands:')
        styled_aliases = [
            toolcli.add_style(alias, styles['command'])
            for alias in cli_alias_utils.get_alias_list()
        ]
        toolcli.print(', '.join(styled_aliases))
        print()
        cli_alias_utils.print_alias_status(alias_status=alias_status, styles=styles)
        print()
        if toolcli.input_yes_or_no(
            'Do you want to install these aliases? ',
            style=styles['question'],
            default='yes',
        ):
            cli_alias_utils.append_aliases_to_shell_configs(confirm=True, verbose=False)
            print()
            print('Aliases installed')
