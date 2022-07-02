import asyncio

import pytest

from ctc import rpc


@pytest.fixture(scope="session")
def event_loop(request):
    """create an instance of the default event loop for each test case

    adapted from https://stackoverflow.com/a/66225169
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session', autouse=True)
async def setup_teardown():

    # setup
    pass

    # transition to teardown
    yield

    # teardown
    await rpc.async_close_http_session()
