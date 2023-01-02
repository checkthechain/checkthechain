from __future__ import annotations

import typing

from ctc import spec
from . import config_validate

if typing.TYPE_CHECKING:
    import toolconfig


def write_config_file(
    config_data: spec.Config,
    path: str,
    *,
    overwrite: toolconfig.OverwriteOption = False,
    style: typing.Optional[str] = None,
    headless: bool = False,
) -> None:
    import toolconfig

    config_validate.validate_config(config_data)

    toolconfig.write_config_file(
        config_data=typing.cast(
            typing.MutableMapping[str, typing.Any],
            config_data,
        ),
        path=path,
        overwrite=overwrite,
        style=style,
        headless=headless,
    )
