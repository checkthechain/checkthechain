from __future__ import annotations

import typing

from ctc import spec

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
