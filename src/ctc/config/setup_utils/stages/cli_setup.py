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

        current_theme_name = cli_utils.get_color_theme_name()
        using_custom_theme = current_theme_name not in cli_utils.color_themes

        print()
        print('Available color themes:')
        color_keys = [
            'title',
            'metavar',
            'description',
            'content',
            'option',
            'comment',
        ]
        cells = []
        if using_custom_theme:
            cell = toolstr.add_style('current', 'bold') + '\n'
            for color_key in color_keys:
                cell += '\n' + toolstr.add_style(
                    color_key, old_color_theme[color_key]  # type: ignore
                )
            cells.append(cell)
        for theme_name, theme_colors in cli_utils.color_themes.items():
            cell = toolstr.add_style(theme_name, 'bold') + '\n'
            for color_key in color_keys:
                cell += '\n' + toolstr.add_style(
                    color_key, theme_colors[color_key]  # type: ignore
                )
            cells.append(cell)
        cells_per_row = 6
        n_rows = _ceil_division(len(cells), cells_per_row)
        rows = [
            cells[r * cells_per_row: (r + 1) * cells_per_row]
            for r in range(n_rows)
        ]
        print()
        toolstr.print_multiline_table(rows)

        choices = list(cli_utils.color_themes.keys())
        if using_custom_theme:
            choices = ['current'] + choices
        choices.append('create custom theme')
        print()
        choice = toolcli.input_number_choice(
            prompt='Which color theme to use? ',
            choices=choices,
            default=choices[0],
        )
        choice_text = choices[choice]
        if choice_text in cli_utils.color_themes:
            new_color_theme = cli_utils.color_themes[choice_text]
        elif choice_text == 'create custom theme':
            new_color_theme = cli_utils.create_custom_color_theme(
                old_color_theme=cli.get_cli_styles(),
                headless=headless,
            )
        else:
            raise Exception('choice error')
        return new_color_theme
    else:
        return old_color_theme


def _ceil_division(a: int, b: int) -> int:
    # from https://stackoverflow.com/a/17511341
    # better than math.ceil because no floating point error
    return -(a // -b)


def _get_cli_chart_charset(
    *,
    styles: toolcli.StyleTheme,
    old_config: typing.Mapping[typing.Any, typing.Any],
    headless: bool,
) -> toolstr.SampleMode:
    return config_defaults.get_default_cli_chart_charset()

