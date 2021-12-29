import sys

import toolcli

from ctc import spec
from .. import config_read


def ensure_valid() -> None:
    if config_read.config_path_exists() and not config_read.config_is_valid():
        print()
        print('Config file already exists but is invalid')
        print()
        print('Config should conform to the following spec:')
        print()
        print('{')
        for key, value in spec.ConfigSpec.__annotations__.items():
            print('    ' + key + ':', value)
        print('}')
        print()
        config_path = config_read.get_config_path(raise_if_dne=False)
        print('File does not conform to spec:', config_path)
        print()
        choices = ['Create new config from scratch', 'Manually repair config']
        answer = toolcli.input_number_choice(
            prompt='How do you want to proceed?',
            choices=choices,
        )
        if answer == 1:
            print(
                'You should manually edit the file and then restart ctc setup'
            )
            sys.exit()

