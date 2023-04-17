from __future__ import annotations

import os
import typing

from ctc import spec
from . import config_validate


def write_config_file(
    config_data: spec.Config,
    path: str,
    *,
    overwrite: typing.Literal[True, False, 'prompt'] = False,
    style: typing.Optional[str] = None,
    headless: bool = False,
) -> None:
    import json

    # validate config data
    config_validate.validate_config(config_data)

    # assert overwrite options
    if os.path.isfile(path):
        if overwrite is True:
            pass
        elif overwrite is False:
            raise Exception('use overwrite=True to overwrite an existing file')
        elif overwrite == 'prompt':
            import toolcli

            if not toolcli.input_yes_or_no(
                prompt='File already exists: '
                + str(path)
                + '\n\nOverwrite file?\n',
                style=style,
            ):
                raise Exception('must overwrite file to proceed')
        else:
            raise Exception('unknown value for overwrite: ' + str(overwrite))

    # write file
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(config_data, f)

