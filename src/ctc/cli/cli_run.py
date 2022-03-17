import os

import toolcli

import ctc


command_index = {
    #
    # admin commands
    (): 'ctc.cli.commands.root_command',
    ('config',): 'ctc.cli.commands.admin.config_command',
    ('config', 'edit'): 'ctc.cli.commands.admin.config.edit_command',
    ('config', 'path'): 'ctc.cli.commands.admin.config.path_command',
    (
        'download-proxy-abi',
    ): 'ctc.cli.commands.admin.download_proxy_abi_command',
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
    # ('events',): 'ctc.cli.commands.data.events_command',
    ('find',): 'ctc.cli.commands.data.find_command',
    ('gas',): 'ctc.cli.commands.data.gas_command',
    ('transaction',): 'ctc.cli.commands.data.transaction_command',
    #
    # protocol commands
    ('cg',): 'ctc.cli.commands.data.cg_command',
    ('chainlink',): 'ctc.protocols.chainlink_utils.cli.chainlink_command',
    ('chainlink', 'ls'): 'ctc.protocols.chainlink_utils.cli.chainlink_ls_command',
    ('curve', 'pools'): 'ctc.protocols.curve_utils.cli.curve_pools_command',
    ('ens',): 'ctc.protocols.ens_utils.cli.ens_command',
    ('ens', 'exists'): 'ctc.protocols.ens_utils.cli.ens.exists_command',
    ('ens', 'hash'): 'ctc.protocols.ens_utils.cli.ens.hash_command',
    ('ens', 'owner'): 'ctc.protocols.ens_utils.cli.ens.owner_command',
    ('ens', 'records'): 'ctc.protocols.ens_utils.cli.ens.records_command',
    ('ens', 'resolve'): 'ctc.protocols.ens_utils.cli.ens.resolve_command',
    ('ens', 'reverse'): 'ctc.protocols.ens_utils.cli.ens.reverse_command',
    ('fei', 'analytics'): 'ctc.protocols.fei_utils.cli.fei.analytics_command',
    ('fei', 'pcv'): 'ctc.protocols.fei_utils.cli.fei.pcv_command',
    (
        'fei',
        'pcv',
        'assets',
    ): 'ctc.protocols.fei_utils.cli.fei.pcv_assets_command',
    (
        'fei',
        'pcv',
        'deposits',
    ): 'ctc.protocols.fei_utils.cli.fei.pcv_deposits_command',
    ('rari',): 'ctc.protocols.rari_utils.cli.rari.fuse_command',
    ('rari', 'pools'): 'ctc.protocols.rari_utils.cli.rari.pools_command',
    # ('uniswap', 'chart'): 'ctc.protocols.uniswap_v2_utils.cli.chart_command',
    ('uniswap', 'mints'): 'ctc.protocols.uniswap_v2_utils.cli.mints_command',
    ('uniswap', 'burns'): 'ctc.protocols.uniswap_v2_utils.cli.burns_command',
    ('uniswap', 'swaps'): 'ctc.protocols.uniswap_v2_utils.cli.swaps_command',
    ('uniswap', 'pool'): 'ctc.protocols.uniswap_v2_utils.cli.pool_command',
    ('4byte',): 'ctc.protocols.fourbyte_utils.cli.fourbyte_command',
    (
        '4byte',
        'build',
    ): 'ctc.protocols.fourbyte_utils.cli.fourbyte_build_command',
    (
        '4byte',
        'path',
    ): 'ctc.protocols.fourbyte_utils.cli.fourbyte_path_command',
}


description = """ctc is a tool for historical data analysis of Ethereum and other EVM chains

if using ctc for the first time, run:
    [option]ctc setup[/option]

for quick lookups of an address, block, tx, or timestamp, run:
    [option]ctc QUERY[/option]"""


cd_dir_help = {
    'code': 'directory where ctc code is stored',
    'data': 'directory where ctc stores data',
    'default_data': 'directory where ctc stores default data',
    'config': 'directory where ctc stores config',
    'notebooks': 'directory where ctc stores notebooks',
}


def cd_dir_getter(dirname: str) -> str:
    import ctc
    import ctc.config

    if dirname == 'code':
        return ctc.__path__[0]

    elif dirname == 'data':
        return ctc.config.get_data_dir()

    elif dirname == 'default_data':
        return ctc.config.get_default_data_dir()

    elif dirname == 'config':
        return os.path.dirname(ctc.config.get_config_path())

    elif dirname == 'notebooks':
        return ctc.config.get_reports_dir()

    else:
        raise Exception('unknown directory: ' + str(dirname))


def run_cli(raw_command=None, **toolcli_kwargs):

    config = {
        #
        # metadata
        'base_command': 'ctc',
        'description': description,
        'version': ctc.__version__,
        'cd_dir_help': cd_dir_help,
        'cd_dir_getter': cd_dir_getter,
        #
        'style_theme': {
            'title': 'bold #ce93f9',
            # 'description': '#f1fa8c',
            # 'metavar': '#8be9fd',
            'description': '#b9f29f',
            'option': '#64aaaa',
            # 'description': '#64aaaa',
            'comment': '#6272a4',
            # 'comment': '#8be9fd',
        },
        #
        # subcommands
        'include_cd_subcommand': True,
        'include_version_subcommand': True,
        'include_help_subcommand': True,
        'include_cli_subcommand': True,
        #
        # args
        'include_debug_arg': True,
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

