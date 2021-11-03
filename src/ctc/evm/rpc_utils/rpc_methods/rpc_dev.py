
def eth_get_compilers(provider=None):
    return rpc_backends.rpc_call(
        method='eth_getCompilers',
        parameters=[],
        provider=provider,
    )


def eth_compile_lll(code, provider=None):
    return rpc_backends.rpc_call(
        method='eth_compileLLL',
        parameters=[code],
        provider=provider,
    )


def eth_compile_solidity(code, provider=None):
    return rpc_backends.rpc_call(
        method='eth_compileSolidity',
        parameters=[code],
        provider=provider,
    )


def eth_compile_serpent(code, provider=None):
    return rpc_backends.rpc_call(
        method='eth_compileSerpent',
        parameters=[code],
        provider=provider,
    )

