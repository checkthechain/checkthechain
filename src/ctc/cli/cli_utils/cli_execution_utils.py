from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import types


class AsyncContextManager:
    """performs cleanup before eventloop is closed"""

    async def __aenter__(self) -> None:
        pass

    async def __aexit__(
        self,
        exception_type: typing.Type[BaseException] | None,
        exception: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        from ctc import rpc

        # TODO: close all sessions, not just default session
        # TODO: close pending db connections
        await rpc.async_close_http_session()
