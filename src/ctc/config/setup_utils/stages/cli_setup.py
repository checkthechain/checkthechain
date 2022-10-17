from __future__ import annotations

import typing

from ctc.config import config_defaults
from ctc import spec


def setup_cli(
    *,
    styles: dict[str, str],
    old_config: typing.Mapping[typing.Any, typing.Any],
    headless: bool,
) -> spec.PartialConfig:
    # TODO: take user input to configure
    return {
        'cli_color_theme': config_defaults.get_default_cli_color_theme(),
        'cli_chart_charset': config_defaults.get_default_cli_chart_charset(),
    }
