import typing

from ctc import spec

import toolconfig


def write_config_file(
    config_data: spec.ConfigSpec,
    path: str,
    overwrite: bool = False,
    style: typing.Optional[str] = None
) -> None:

    toolconfig.write_config_file(
        config_data=typing.cast(
            typing.MutableMapping[str, typing.Any],
            config_data,
        ),
        path=path,
        overwrite=overwrite,
        style=style,
    )

