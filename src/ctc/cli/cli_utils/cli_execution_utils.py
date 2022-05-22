
class AsyncContextManager:
    """performs cleanup before eventloop is closed"""

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc, tb):
        from ctc import rpc

        # TODO: close all sessions, not just default session
        # TODO: close pending db connections
        await rpc.async_close_http_session()
