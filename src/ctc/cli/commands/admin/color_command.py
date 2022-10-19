from __future__ import annotations

import toolcli
import toolstr

from ctc import cli
from ctc.cli import cli_utils


def get_command_spec() -> toolcli.CommandSpec:
    styles = cli.get_cli_styles()
    return {
        'f': color_command,
        'help': 'display or set color themes',
        'args': [
            {
                'name': 'theme',
                'help': 'color theme to set, '
                + toolstr.add_style('default', styles['option'])
                + ' to reset, '
                + toolstr.add_style('custom', styles['option'])
                + ' to customize',
                'nargs': '?',
            },
            {
                'name': ['-v', '--verbose'],
                'help': 'display available color themes',
                'action': 'store_true',
            },
        ],
        'examples': [
            '',
            'nord',
            '-v',
        ],
    }


def color_command(theme: str | None, verbose: bool) -> None:

    styles = cli.get_cli_styles()

    if theme is not None:
        if theme in ['default', 'reset']:
            cli_utils.reset_color_theme()
        elif theme == 'custom':
            print('setting custom color theme')
            styles = cli_utils.create_custom_color_theme()
            cli_utils.set_color_theme(styles)
        else:
            print('setting color theme to:', theme)
            styles = cli_utils.set_color_theme(theme)
        toolstr.print_text_box('Color Theme', style=styles['title'])
        cli_utils.print_color_theme(styles)

    elif verbose:
        cli_utils.preview_color_themes()
        print()
        toolstr.print(
            'enable a theme with '
            + toolstr.add_style(
                'ctc color <theme_name>', styles['option'] + ' bold'
            ),
            style=styles['comment'],
        )

    else:
        toolstr.print_text_box('Color Theme', style=styles['title'])
        cli_utils.print_color_theme(styles)
        print()
        toolstr.print(
            'to view available color themes, use '
            + toolstr.add_style('ctc color -v', styles['option']),
            style=styles['comment'],
        )
        print()
        toolstr.print(
            'to set a color theme, use '
            + toolstr.add_style('ctc color <theme>', styles['option']),
            style=styles['comment'],
        )
        toolstr.print(
            '    where '
            + toolstr.add_style('<theme>', styles['option'])
            + ' is a theme name or theme specification',
            style=styles['comment'],
        )
        print()
        toolstr.print(
            'to reset to the default color theme, use '
            + toolstr.add_style('ctc color default', styles['option']),
            style=styles['comment'],
        )
