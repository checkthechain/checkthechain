import toolcli


def run_cli(raw_command=None, **toolcli_kwargs):

    command_index = {
        (): 'ctc.cli.root_command',
        ('add_proxy_abi',): 'ctc.cli.commands.add_proxy_abi_command',
        ('address',): 'ctc.cli.commands.address_command',
        ('block',): 'ctc.cli.commands.block_command',
        ('call',): 'ctc.cli.commands.call_command',
        ('cd',): 'ctc.cli.commands.cd_command',
        ('chainlink',): 'ctc.protocols.chainlink_utils.chainlink_command',
        ('config', 'create'): 'ctc.cli.commands.config.create_command',
        ('config', 'edit'): 'ctc.cli.commands.config.edit_command',
        ('config',): 'ctc.cli.commands.config_command',
        ('fei', 'payload'): 'ctc.protocols.fei_utils.cli.fei.payload_command',
        ('fei',): 'ctc.protocols.fei_utils.cli.fei_command',
        ('gas',): 'ctc.cli.commands.gas_command',
        ('keccak',): 'ctc.cli.commands.keccak_command',
        ('rari', 'fuse'): 'ctc.protocols.rari_utils.cli.rari.fuse_command',
        ('rechunk_events',): 'ctc.cli.commands.rechunk_command',
        ('setup',): 'ctc.cli.commands.setup_command',
        ('token',): 'ctc.cli.commands.token_command',
        ('transaction',): 'ctc.cli.commands.transaction_command',
    }

    config = {'include_cd': True, 'include_debug': True}
    toolcli_kwargs = {'config': config}

    toolcli.run_cli(
        raw_command=raw_command,
        command_index=command_index,
        **toolcli_kwargs
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

