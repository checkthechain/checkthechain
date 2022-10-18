from __future__ import annotations

import typing

import toolcli
import toolstr

from ctc import cli
from ctc import spec
from ctc.config import config_defaults


def setup_cli(
    *,
    styles: toolcli.StyleTheme,
    old_config: typing.Mapping[typing.Any, typing.Any],
    headless: bool,
) -> spec.PartialConfig:

    print()
    print()
    toolstr.print('## CLI Customization', style=styles['title'])

    print()
    cli_color_theme = _get_cli_color_theme(
        styles=styles,
        old_config=old_config,
        headless=headless,
    )
    print()
    cli_chart_charset = _get_cli_chart_charset(
        styles=styles,
        old_config=old_config,
        headless=headless,
    )

    return {
        'cli_color_theme': cli_color_theme,
        'cli_chart_charset': cli_chart_charset,
    }


def _get_cli_color_theme(
    *,
    styles: toolcli.StyleTheme,
    old_config: typing.Mapping[typing.Any, typing.Any],
    headless: bool,
) -> toolcli.StyleTheme:

    old_color_theme = old_config.get('cli_color_theme')
    if old_color_theme is None:
        old_color_theme = config_defaults.get_default_cli_color_theme()

    print('Current color theme:')
    for key, value in old_color_theme.items():
        cli.print_bullet(
            key=key,
            value=toolstr.add_style(str(value), str(value)),
            key_style='',
        )
    print()
    answer = toolcli.input_yes_or_no(
        'Modify this theme? ',
        default='no',
        style=styles['metavar'],
        headless=headless,
    )
    if answer:
        from ctc.cli import cli_utils

        new_color_theme = cli_utils.create_custom_color_theme(
            old_color_theme=cli.get_cli_styles(),
            headless=headless,
        )
        return new_color_theme
    else:
        return old_color_theme


def _get_cli_chart_charset(
    *,
    styles: toolcli.StyleTheme,
    old_config: typing.Mapping[typing.Any, typing.Any],
    headless: bool,
) -> toolstr.SampleMode:
    return config_defaults.get_default_cli_chart_charset()
