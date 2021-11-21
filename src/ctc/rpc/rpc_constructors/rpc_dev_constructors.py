from .. import rpc_request


def construct_eth_get_compilers():
    return rpc_request.create('eth_getCompilers', [])


def construct_eth_compile_lll(code):
    return rpc_request.create('eth_compileLLL', [code])


def construct_eth_compile_solidity(code):
    return rpc_request.create('eth_compileSolidity', [code])


def construct_eth_compile_serpent(code):
    return rpc_request.create('eth_compileSerpent', [code])

