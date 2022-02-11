from __future__ import annotations

import sys

import toolcli

from ctc import spec
from .. import config_read


def ensure_valid(styles: dict[str, str]) -> None:
    if config_read.config_path_exists() and not config_read.config_is_valid():
        print()
        print()
        toolcli.print('## Current Config Validation', style=styles['header'])
        print()
        print('Config file already exists but is invalid')
        print()
        print('Config should conform to the following spec:')
        print()
        toolcli.print('{', style=styles['quote'])
        for key, value in spec.ConfigSpec.__annotations__.items():
            toolcli.print(
                '    ' + key + ':',
                value,
                highlight=False,
                style=styles['quote'],
            )
        toolcli.print('}', style=styles['quote'])
        print()
        config_path = config_read.get_config_path(raise_if_dne=False)
        toolcli.print(
            'Spec is violated in current config file:',
            toolcli.add_style(config_path, styles['path']),
        )
        print()
        choices = ['Create new config from scratch', 'Manually repair config']
        answer = toolcli.input_number_choice(
            prompt='How do you want to proceed?',
            choices=choices,
            style=styles['question'],
        )
        if answer == 1:
            print(
                'You should manually edit the file and then restart ctc setup'
            )
            sys.exit()

