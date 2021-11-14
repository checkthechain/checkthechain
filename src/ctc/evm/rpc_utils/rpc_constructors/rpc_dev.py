from .. import rpc_crud


def construct_eth_get_compilers():
    return rpc_crud.construct_rpc_call('eth_getCompilers', [])


def construct_eth_compile_lll(code):
    return rpc_crud.construct_rpc_call('eth_compileLLL', [code])


def construct_eth_compile_solidity(code):
    return rpc_crud.construct_rpc_call('eth_compileSolidity', [code])


def construct_eth_compile_serpent(code):
    return rpc_crud.construct_rpc_call('eth_compileSerpent', [code])

