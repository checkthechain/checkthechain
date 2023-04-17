from __future__ import annotations

import os
import typing

import toolstr

import ctc.config
from ctc.config import config_defaults

from . import cli_output_utils

if typing.TYPE_CHECKING:
    import toolcli

    StyleThemeReference = typing.Union[str, toolcli.StyleTheme]


color_themes: typing.Mapping[str, toolcli.StyleTheme] = {
    'apparatus': {
        # https://github.com/sslivkoff/apparatus-color-scheme
        # https://github.com/arcticicestudio/nord-vim/blob/main/colors/nord.vim
        'title': 'bold #ce93f9',
        'metavar': '#8be9fd',
        'description': '#b9f29f',
        'content': '#f1fa8c',
        'option': '#64aaaa',
        'comment': '#6272a4',
    },
    'nord': {
        # https://www.nordtheme.com/docs/colors-and-palettes
        'title': 'bold #88c0d0',
        'metavar': '#e5e9f0',
        'description': '#8fbcbb',
        'content': '#81a1c1',
        'option': '#5e81ac',
        'comment': '#aaaaaa',
    },
    # 'solarized': {
    #     # https://en.wikipedia.org/wiki/Solarized#Colors
    #     'title': 'bold #cb4b16',
    #     'metavar': '#268bd2',
    #     'description': '#859900',
    #     'content': '#6c71c4',
    #     'option': '#2aa198',
    #     'comment': '#657b83',
    # },
    'neonwolf': {
        # https://github.com/h3xx/tig-colors-neonwolf/blob/flair/screenshots/sample.png
        'title': 'bold #afff00',
        'metavar': '#5ccef4',
        'description': '#00afff',
        'content': '#ff0000',
        'option': '#d700ff',
        'comment': '#b2b2b2',
    },
    'monokai': {
        'title': 'bold #f92672',
        'metavar': '#a6e22e',
        'option': '#66d9ef',
        'description': '#fc9867',
        'content': '#ae81ff',
        'comment': '#88846f',
        # 'title': 'bold #66d9ef',
        # 'metavar': '#a6e22e',
        # 'option': '#e87d3e',
        # 'description': '#f92672',
        # 'content': '#ae81ff',
        # 'comment': '',
    },
    # 'oceanic': {
    #     # https://github.com/mhartington/oceanic-next
    #     'title': 'bold #fac863',
    #     'metavar': '#fac863',
    #     'option': '#fac863',
    #     'description': '#99c794',
    #     'content': '#c594c5',
    #     'comment': '#c594c5',
    #     # 'comment': '#6090c0',
    #     # 'metavar': '#ec5f67',
    #     # palenight seems similar https://github.com/drewtempelmeyer/palenight.vim/blob/master/images/screenshot.png
    # },
    # tokyo night https://github.com/folke/tokyonight.nvim
    # sonokai https://github.com/sainnhe/sonokai
    # '': {
    #     'title': 'bold ',
    #     'metavar': '',
    #     'option': '',
    #     'description': '',
    #     'content': '',
    #     'comment': '',
    # },
    # '': {
    #     'title': 'bold ',
    #     'metavar': '',
    #     'option': '',
    #     'description': '',
    #     'content': '',
    #     'comment': '',
    # },
    # '': {
    #     'title': 'bold ',
    #     'metavar': '',
    #     'option': '',
    #     'description': '',
    #     'content': '',
    #     'comment': '',
    # },
    # light themes
    # ayu https://github.com/ayu-theme/ayu-vim
    # solarized-light https://github.com/romainl/flattened
}


def get_cli_styles(color: bool | None = None) -> toolcli.StyleTheme:

    # if in notebook, do not use styles
    color = not _is_jupyter_notebook()

    if color:
        config_theme = ctc.config.get_cli_color_theme()

        # ensure that all keys are present
        config_theme = {
            'title': config_theme.get('title', ''),
            'metavar': config_theme.get('metavar', ''),
            'description': config_theme.get('description', ''),
            'content': config_theme.get('content', ''),
            'option': config_theme.get('option', ''),
            'comment': config_theme.get('comment', ''),
        }

        return config_theme

    else:
        return {
            'title': '',
            'metavar': '',
            'description': '',
            'content': '',
            'option': '',
            'comment': '',
        }


def get_color_theme_name() -> str:
    config_theme = ctc.config.get_cli_color_theme()
    for other_name, other_theme in color_themes.items():
        if other_theme == config_theme:
            return other_name
    else:
        return 'custom'


def _is_jupyter_notebook() -> bool:
    """adapted from https://gist.github.com/thomasaarholt/e5e2da71ea3ee412616b27d364e3ae82"""
    import sys

    if 'jupyter_client' not in sys.modules:
        return False

    try:
        from IPython import get_ipython

        if 'IPKernelApp' not in get_ipython().config:  # type: ignore
            raise ImportError("console")
            return False
        if 'VSCODE_PID' in os.environ:
            raise ImportError("vscode")
            return False
    except Exception:
        return False
    else:
        return True


def print_color_theme(color_theme: toolcli.StyleTheme) -> None:
    import toolstr

    for key, value in color_theme.items():
        cli_output_utils.print_bullet(
            key=key,
            value=toolstr.add_style(str(value), str(value)),
            key_style='',
        )


def set_color_theme(theme: StyleThemeReference) -> toolcli.StyleTheme:

    import json

    styles = resolve_color_theme_reference(theme)
    config_path = ctc.config.get_config_path()
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    new_config_data = dict(config_data, cli_color_theme=styles)
    with open(config_path, 'w') as f:
        json.dump(new_config_data, f)
    print('color theme updated')

    return styles


def resolve_color_theme_reference(
    theme: StyleThemeReference | toolcli.StyleTheme,
) -> toolcli.StyleTheme:
    if isinstance(theme, str):
        if theme in ['default', 'reset']:
            styles = config_defaults.get_default_cli_color_theme()
        elif theme in color_themes:
            styles = color_themes[theme]
        else:
            raise Exception('unknown color theme: ' + str(theme))
    elif isinstance(theme, dict):
        styles = theme
    else:
        raise Exception('unknown theme format: ' + str(theme))

    return styles


def reset_color_theme() -> toolcli.StyleTheme:
    return set_color_theme('default')


def create_custom_color_theme(
    old_color_theme: toolcli.StyleTheme | None = None,
    headless: bool = False,
) -> toolcli.StyleTheme:

    import toolcli
    import toolstr

    if old_color_theme is None:
        old_color_theme = {
            'title': '',
            'metavar': '',
            'description': '',
            'content': '',
            'option': '',
            'comment': '',
        }

    new_color_theme: toolcli.StyleTheme = {
        'title': '',
        'metavar': '',
        'description': '',
        'content': '',
        'option': '',
        'comment': '',
    }
    for key, value in old_color_theme.items():
        style = toolcli.input_prompt(
            'What style to use for ' + toolstr.add_style(key, 'bold') + '? ',
            style=old_color_theme.get('metavar'),
            default='"' + toolstr.add_style(str(value), str(value)) + '"',
            headless=headless,
        )
        new_color_theme[key] = style  # type: ignore

    return new_color_theme


def preview_color_themes(
    themes: typing.Sequence[StyleThemeReference]
    | typing.Mapping[str, StyleThemeReference]
    | None = None,
) -> None:

    if themes is None:
        themes = color_themes

    theme_names = []
    theme_list = []
    if isinstance(themes, list):
        theme_names = [str(i + 1) for i in range(len(themes))]
        theme_list = [resolve_color_theme_reference(theme) for theme in themes]
    elif isinstance(themes, dict):
        theme_names = list(themes.keys())
        theme_list = [
            resolve_color_theme_reference(theme) for theme in themes.values()
        ]
    else:
        raise Exception()

    rows = []
    for theme_name, theme in zip(theme_names, theme_list):
        styled_names = []
        styled_styles = []
        for style_name, obj_style in theme.items():
            style = typing.cast(str, obj_style)
            styled_names.append(toolstr.add_style(style_name, style))
            styled_styles.append(toolstr.add_style(style, style))
        styles = '\n'.join(styled_names)
        row = [theme_name, styles, styled_styles]
        rows.append(row)
    labels = ['theme', 'labels', 'colors']
    toolstr.print_multiline_table(
        rows,
        labels=labels,
        label_style='bold',
        border='#666666',
    )
