from __future__ import annotations

import typing

import toolcli
import toolstr

from ctc.cli.cli_utils import cli_alias_utils


def add_cli_aliases(
    *, styles: typing.Mapping[str, str], headless: bool, skip_aliases: bool
) -> None:

    print()
    print()
    toolstr.print('## Installing CLI Aliases', style=styles['header'])

    alias_status = cli_alias_utils.get_paths_alias_status()
    current = all(status == 'current' for status in alias_status.values())

    if current:
        print()
        cli_alias_utils.print_alias_status(include_title=False)
    else:
        print()
        cli_alias_utils.print_paths_alias_status()
        print()
        print(
            'ctc can install cli aliases to make many commands quicker to type'
        )
        print()
        toolstr.print(
            'For example, you can type '
            + toolstr.add_style('4byte 0xa9059cbb', styles['command'])
            + ' instead of '
            + toolstr.add_style('ctc 4byte 0xa9059cbb', styles['command'])
        )
        print()
        print('ctc has aliases prepared for the following commands:')
        print()
        cli_alias_utils.print_aliases()
        print()

        if skip_aliases:
            default = 'no'
        else:
            default = 'yes'

        if toolcli.input_yes_or_no(
            'Do you want to install these aliases? ',
            style=styles['question'],
            default=default,
            headless=headless,
        ):
            cli_alias_utils.install_aliases(confirm=True, headless=headless)
            print()
            print('Aliases installed')
