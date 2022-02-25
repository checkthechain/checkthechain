import toolcli

command_index = {
    #
    # admin commands
    (): 'ctc.cli.commands.root_command',
    ('cd',): 'ctc.cli.commands.admin.cd_command',
    ('config',): 'ctc.cli.commands.admin.config_command',
    ('config', 'edit'): 'ctc.cli.commands.admin.config.edit_command',
    ('config', 'path'): 'ctc.cli.commands.admin.config.path_command',
    ('download-proxy-abi',): 'ctc.cli.commands.admin.download_proxy_abi_command',
    ('setup',): 'ctc.cli.commands.admin.setup_command',
    ('rechunk-events',): 'ctc.cli.commands.admin.rechunk_command',
    #
    # compute commands
    ('checksum',): 'ctc.cli.commands.compute.checksum_command',
    ('keccak',): 'ctc.cli.commands.compute.keccak_command',
    ('lower',): 'ctc.cli.commands.compute.lower_command',
    ('ascii',): 'ctc.cli.commands.compute.ascii_command',
    ('hex',): 'ctc.cli.commands.compute.hex_command',
    #
    # data commands
    ('address',): 'ctc.cli.commands.data.address_command',
    ('block',): 'ctc.cli.commands.data.block_command',
    ('blocks',): 'ctc.cli.commands.data.blocks_command',
    ('call',): 'ctc.cli.commands.data.call_command',
    ('calls',): 'ctc.cli.commands.data.calls_command',
    ('eth', 'balance'): 'ctc.cli.commands.data.eth.balance_command',
    ('eth', 'balances'): 'ctc.cli.commands.data.eth.balances_command',
    ('erc20', 'balance'): 'ctc.cli.commands.data.erc20.balance_command',
    ('erc20', 'balances'): 'ctc.cli.commands.data.erc20.balances_command',
    ('erc20', 'transfers'): 'ctc.cli.commands.data.erc20.transfers_command',
    ('events',): 'ctc.cli.commands.data.events_command',
    ('find',): 'ctc.cli.commands.data.find_command',
    ('gas',): 'ctc.cli.commands.data.gas_command',
    ('transaction',): 'ctc.cli.commands.data.transaction_command',
    #
    # protocol commands
    ('chainlink',): 'ctc.protocols.chainlink_utils.cli.chainlink_command',
    ('ens',): 'ctc.protocols.ens_utils.cli.ens_command',
    ('ens', 'exists'): 'ctc.protocols.ens_utils.cli.ens.exists_command',
    ('ens', 'hash'): 'ctc.protocols.ens_utils.cli.ens.hash_command',
    ('ens', 'owner'): 'ctc.protocols.ens_utils.cli.ens.owner_command',
    ('ens', 'records'): 'ctc.protocols.ens_utils.cli.ens.records_command',
    ('ens', 'resolve'): 'ctc.protocols.ens_utils.cli.ens.resolve_command',
    ('ens', 'reverse'): 'ctc.protocols.ens_utils.cli.ens.reverse_command',
    ('fei', 'analytics'): 'ctc.protocols.fei_utils.cli.fei.analytics_command',
    ('fei', 'pcv'): 'ctc.protocols.fei_utils.cli.fei.pcv_command',
    ('fei', 'pcv', 'assets'): 'ctc.protocols.fei_utils.cli.fei.pcv_assets_command',
    ('fei', 'pcv', 'deposits'): 'ctc.protocols.fei_utils.cli.fei.pcv_deposits_command',
    ('rari', 'fuse'): 'ctc.protocols.rari_utils.cli.rari.fuse_command',
    ('uniswap', 'mints'): 'ctc.protocols.uniswap_v2_utils.cli.mints_command',
    ('uniswap', 'burns'): 'ctc.protocols.uniswap_v2_utils.cli.burns_command',
    ('uniswap', 'swaps'): 'ctc.protocols.uniswap_v2_utils.cli.swaps_command',
    ('uniswap', 'pool'): 'ctc.protocols.uniswap_v2_utils.cli.pool_command',
}


def run_cli(raw_command=None, **toolcli_kwargs):

    config = {
        'include_cd': True,
        'include_debug': True,
    }
    toolcli_kwargs = dict({'config': config}, **toolcli_kwargs)

    toolcli.run_cli(
        raw_command=raw_command,
        command_index=command_index,
        **toolcli_kwargs,
    )


#
# # old
#


def create_ctc_cli():

    # hardcode this for speed
    # command_indices = {}
    # roots = [
    #     'ctc.cli.commands',
    #     'ctc.protocols.fei_utils.cli',
    # ]
    # for root in roots:
    #     branch = toolcli.autoindex_command_root(root_module_name=root)
    #     overlap = set(branch.keys()).intersection(command_indices.keys())
    #     if len(overlap) > 0:
    #         raise Exception('command_index key collision: ' + str(overlap))
    #     command_indices.update(branch)
    # print('command_indices:', command_indices)
    command_indices = {
        'ctc.cli.commands': [
            ('block',),
            ('gas',),
            ('transaction',),
            ('address',),
            ('token',),
            ('call',),
        ],
        'ctc.protocols.fei_utils.cli': [('fei', 'eth')],
        'ctc.protocols.chainlink_utils.cli': [('chainlink',)],
        'ctc.protocols.rari_utils.cli': [('rari', 'fuse')],
    }

    cli = toolcli.BaseCLI(
        command_indices=command_indices,
        passthrough_command=passthrough_command,
    )
    return cli


def passthrough_command(command):

    arg = command[1]

    if len(arg) <= 9 and str.isnumeric(arg):
        return 'block'

    elif arg.startswith('0x') and len(arg) == 66:
        return 'transaction'

    elif arg.startswith('0x') and len(arg) == 42:
        return 'address'

    elif str.isalnum(arg) and len(arg) <= 8:
        return 'token'

    else:
        raise Exception('could not determine command')

