# from __future__ import annotations

# import asyncio

# import toolcli

# from ctc import evm
# from ctc import rpc
# from ctc import spec


# def get_command_spec() -> toolcli.CommandSpec:
#     return {
#         'f': add_proxy_abi_comamand,
#         'help': 'download proxy abi for contract',
#         'args': [
#             {
#                 'name': 'contract_address',
#                 'help': 'address that points toward implementation',
#             },
#             {
#                 'name': 'implementation_address',
#                 'help': 'address that implements functionality',
#             },
#         ],
#         'examples': [
#             '0xd8553552f8868c1ef160eedf031cf0bcf9686945 0x67db14e73c2dce786b5bbbfa4d010deab4bbfcf9',
#         ],
#     }


# def add_proxy_abi_comamand(
#     contract_address: spec.Address,
#     implementation_address: spec.Address,
# ) -> None:
#     print('saving proxy contract implementation...')
#     print('     for contract:', contract_address)
#     print('   implementation:', implementation_address)
#     answer = input('continue? ')
#     if answer not in ['y', 'yes']:
#         print('aborting')
#         return
#     else:
#         asyncio.run(run(contract_address, implementation_address))


# async def run(
#     contract_address: spec.Address, implementation_address: spec.Address
# ) -> None:
#     await evm.async_save_proxy_contract_abi_to_filesystem(
#         contract_address=contract_address,
#         proxy_implementation=implementation_address,
#     )

#     from ctc.rpc.rpc_backends import rpc_http_async

#     provider = rpc.get_provider()
#     await rpc_http_async.async_close_http_session(provider=provider)

