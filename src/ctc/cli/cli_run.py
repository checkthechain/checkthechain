from __future__ import annotations

import os
import typing

if typing.TYPE_CHECKING:
    import toolsql

    import mypy_extensions

import toolcli

import ctc
from .plugins import toolsql_plugin
from . import cli_utils


command_index_by_category: dict[str, toolcli.CommandIndex] = {
    'admin': {
        (): 'ctc.cli.commands.root_command',
        ('aliases',): 'ctc.cli.commands.admin.aliases_command',
        ('config',): 'ctc.cli.commands.admin.config_command',
        ('config', 'edit'): 'ctc.cli.commands.admin.config.edit_command',
        ('config', 'path'): 'ctc.cli.commands.admin.config.path_command',
        ('db',): 'ctc.cli.commands.admin.db.status_command',
        (
            'db',
            'create',
            'tables',
        ): 'ctc.cli.commands.admin.db.create_tables_command',
        ('db', 'drop'): 'ctc.cli.commands.admin.db.drop_command',
        ('log',): 'ctc.cli.commands.admin.log_command',
        ('setup',): 'ctc.cli.commands.admin.setup_command',
        ('rechunk-events',): 'ctc.cli.commands.admin.rechunk_command',
        ('chains',): 'ctc.cli.commands.admin.chains_command',
    },
    'compute': {
        ('ascii',): 'ctc.cli.commands.compute.ascii_command',
        (
            'create',
            'address',
        ): 'ctc.cli.commands.compute.create_address_command',
        ('checksum',): 'ctc.cli.commands.compute.checksum_command',
        ('decode', 'call'): 'ctc.cli.commands.compute.decode_call_command',
        ('decode',): 'ctc.cli.commands.compute.decode_command',
        ('encode',): 'ctc.cli.commands.compute.encode_command',
        ('hex',): 'ctc.cli.commands.compute.hex_command',
        ('int',): 'ctc.cli.commands.compute.integer_command',
        ('keccak',): 'ctc.cli.commands.compute.keccak_command',
        ('limits',): 'ctc.cli.commands.compute.limits_command',
        ('lower',): 'ctc.cli.commands.compute.lower_command',
        ('rlp', 'encode'): 'ctc.cli.commands.compute.rlp_encode',
        ('selector',): 'ctc.cli.commands.compute.selector_command',
    },
    'data': {
        ('abi',): 'ctc.cli.commands.data.abi_command',
        ('abi', 'diff'): 'ctc.cli.commands.data.abi_diff_command',
        ('address',): 'ctc.cli.commands.data.address_command',
        ('address', 'txs'): 'ctc.cli.commands.data.address_txs_command',
        ('bytecode',): 'ctc.cli.commands.data.bytecode_command',
        ('block',): 'ctc.cli.commands.data.block_command',
        ('blocks',): 'ctc.cli.commands.data.blocks_command',
        ('call',): 'ctc.cli.commands.data.call_command',
        ('call', 'all'): 'ctc.cli.commands.data.call_all_command',
        ('calls',): 'ctc.cli.commands.data.calls_command',
        ('chain',): 'ctc.cli.commands.data.chain_command',
        ('decompile',): 'ctc.cli.commands.data.decompile_command',
        ('dex', 'chart'): 'ctc.cli.commands.data.dex.chart_command',
        ('dex', 'pool'): 'ctc.cli.commands.data.dex.pool_command',
        ('dex', 'pools'): 'ctc.cli.commands.data.dex.pools_command',
        ('dex', 'trades'): 'ctc.cli.commands.data.dex.trades_command',
        ('eth', 'balance'): 'ctc.cli.commands.data.eth.balance_command',
        ('eth', 'balances'): 'ctc.cli.commands.data.eth.balances_command',
        ('erc20',): 'ctc.cli.commands.data.erc20_command',
        ('erc20', 'balance'): 'ctc.cli.commands.data.erc20.balance_command',
        ('erc20', 'balances'): 'ctc.cli.commands.data.erc20.balances_command',
        ('erc20', 'transfers'): 'ctc.cli.commands.data.erc20.transfers_command',
        ('events',): 'ctc.cli.commands.data.events_command',
        ('gas',): 'ctc.cli.commands.data.gas_command',
        ('proxy',): 'ctc.cli.commands.data.proxy_command',
        ('proxy', 'register'): 'ctc.cli.commands.data.proxy_register_command',
        ('storage',): 'ctc.cli.commands.data.storage_command',
        ('symbol',): 'ctc.cli.commands.data.symbol_command',
        ('timestamp',): 'ctc.cli.commands.data.timestamp_command',
        ('tx',): 'ctc.cli.commands.data.tx_command',
    },
    'protocol': {
        ('aave',): 'ctc.protocols.aave_v2_utils.cli.aave_command',
        (
            'aave',
            'addresses',
        ): 'ctc.protocols.aave_v2_utils.cli.aave_addresses_command',
        ('cg',): 'ctc.protocols.coingecko_utils.cli.cg_command',
        ('chainlink',): 'ctc.protocols.chainlink_utils.cli.chainlink_command',
        (
            'chainlink',
            'feeds',
        ): 'ctc.protocols.chainlink_utils.cli.chainlink_ls_command',
        ('curve', 'pools'): 'ctc.protocols.curve_utils.cli.curve_pools_command',
        ('ens',): 'ctc.protocols.ens_utils.cli.ens_command',
        ('ens', 'exists'): 'ctc.protocols.ens_utils.cli.ens.exists_command',
        ('ens', 'hash'): 'ctc.protocols.ens_utils.cli.ens.hash_command',
        ('ens', 'owner'): 'ctc.protocols.ens_utils.cli.ens.owner_command',
        ('ens', 'records'): 'ctc.protocols.ens_utils.cli.ens.records_command',
        ('ens', 'resolve'): 'ctc.protocols.ens_utils.cli.ens.resolve_command',
        ('ens', 'reverse'): 'ctc.protocols.ens_utils.cli.ens.reverse_command',
        ('etherscan',): 'ctc.protocols.etherscan_utils.cli.etherscan_command',
        (
            'fei',
            'analytics',
        ): 'ctc.protocols.fei_utils.cli.fei.analytics_command',
        ('fei', 'depth'): 'ctc.protocols.fei_utils.cli.fei.depth_command',
        ('fei', 'dex'): 'ctc.protocols.fei_utils.cli.fei.dex_command',
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
        ('fei', 'psms'): 'ctc.protocols.fei_utils.cli.fei.psms_command',
        ('gnosis',): 'ctc.protocols.gnosis_utils.cli.gnosis_command',
        ('llama',): 'ctc.protocols.llama_utils.cli.llama_command',
        ('llama', 'chain'): 'ctc.protocols.llama_utils.cli.llama_chain_command',
        (
            'llama',
            'chains',
        ): 'ctc.protocols.llama_utils.cli.llama_chains_command',
        (
            'llama',
            'protocol',
        ): 'ctc.protocols.llama_utils.cli.llama_protocol_command',
        (
            'llama',
            'protocols',
        ): 'ctc.protocols.llama_utils.cli.llama_protocols_command',
        ('llama', 'pool'): 'ctc.protocols.llama_utils.cli.llama_pool_command',
        ('llama', 'pools'): 'ctc.protocols.llama_utils.cli.llama_pools_command',
        ('rari',): 'ctc.protocols.rari_utils.cli.rari.fuse_command',
        ('rari', 'pools'): 'ctc.protocols.rari_utils.cli.rari.pools_command',
        (
            'uniswap',
            'chart',
        ): 'ctc.protocols.uniswap_v2_utils.cli.chart_command',
        (
            'uniswap',
            'mints',
        ): 'ctc.protocols.uniswap_v2_utils.cli.mints_command',
        (
            'uniswap',
            'burns',
        ): 'ctc.protocols.uniswap_v2_utils.cli.burns_command',
        (
            'uniswap',
            'swaps',
        ): 'ctc.protocols.uniswap_v2_utils.cli.swaps_command',
        ('uniswap', 'pool'): 'ctc.protocols.uniswap_v2_utils.cli.pool_command',
        ('yearn',): 'ctc.protocols.yearn_utils.cli.yearn_command',
        (
            'yearn',
            'addresses',
        ): 'ctc.protocols.yearn_utils.cli.yearn_addresses_command',
        ('4byte',): 'ctc.protocols.fourbyte_utils.cli.fourbyte_command',
        (
            '4byte',
            'build',
        ): 'ctc.protocols.fourbyte_utils.cli.fourbyte_build_command',
    },
}

command_index: typing.MutableMapping[toolcli.CommandSequence, toolcli.CommandSpecReference] = {}
help_subcommand_categories = {}
for category, category_command_index in command_index_by_category.items():
    command_index.update(category_command_index)
    for subcommand in category_command_index.keys():
        help_subcommand_categories[subcommand] = category


description = """ctc is a tool for historical data analysis of Ethereum and other EVM chains

if using ctc for the first time, run:
    [option]ctc setup[/option]

for quick lookups of an address, block, tx, or timestamp, run:
    [option]ctc QUERY[/option]

    where [option]QUERY[/option] is an address, block number, tx hash, or timestamp"""

# for example...
#     [description]print block summary[/description]
#     [option]ctc 14000000[/option]

#     [description]print contract summary[/description]
#     [option]ctc 0x956f47f50a910163d8bf957cf5846d573e7f87ca[/option]

#     [description]print token summary[/description]
#     [option]ctc FEI[/option]

#     [description]print tx summary[/description]
#     [option]ctc 0x285117fc6ecd443fc2a39f72dd3df79e65d25c5d3d680d41f229e793a495ef99[/option]"""


cd_dir_help = {
    'code': 'directory where ctc code is stored',
    'data': 'directory where ctc stores data',
    'config': 'directory where ctc stores config',
}


def cd_dir_getter(dirname: str) -> str:
    import ctc
    import ctc.config

    if dirname == 'code':
        return ctc.__path__[0]

    elif dirname == 'data':
        return ctc.config.get_data_dir()

    elif dirname == 'config':
        return os.path.dirname(ctc.config.get_config_path())

    else:
        raise Exception('unknown directory: ' + str(dirname))


if os.environ.get('BUILDING_SPHINX') != '1':
    help_url_getter: None | typing.Callable[
        [
            mypy_extensions.NamedArg(tuple[str, ...], 'subcommand'),
            mypy_extensions.NamedArg(toolcli.ParseSpec, 'parse_spec'),
        ],
        str,
    ] = None
else:

    def help_url_getter(
        *,
        subcommand: typing.Tuple[str, ...],
        parse_spec: toolcli.ParseSpec,
    ) -> str:
        categories = parse_spec['config']['help_subcommand_categories']
        category = categories.get(subcommand, 'other')
        return (
            'https://ctc.readthedocs.io/en/latest/cli/subcommands/'
            + category
            + '/'
            + '_'.join(subcommand)
            + '.html'
        )


def _db_config_getter() -> toolsql.DBConfig | None:
    import ctc.config

    return ctc.config.get_db_config()


# def _is_root_help(raw_command):
#     import sys

#     for command in [raw_command, sys.argv]:
#         if command is None:
#             continue
#         if '--cd-destination-tempfile' in command:
#             index = command.index('--cd-destination-tempfile')
#             command = command[:index] + command[index + 2 :]
#         if all(item.startswith('-') for item in command[1:]):
#             return True
#     return False


# def _print_help_from_cache(command_index, help_cache_dir):
#     help_cache_path = get_help_dir_hash_path(command_index, help_cache_dir)
#     if os.path.isfile(help_cache_path):
#         with open(help_cache_path, 'r') as f:
#             contents = f.read()
#         print(contents, end='')
#         return True
#     else:
#         return False


# def get_help_dir_hash_path(command_index, help_cache_dir):
#     import hashlib

#     command_index_str = str(sorted(command_index.items()))
#     name_hash = hashlib.md5(command_index_str.encode()).hexdigest()
#     help_cache_path = os.path.join(help_cache_dir, name_hash)
#     return help_cache_path


def get_cli_styles() -> toolcli.StyleTheme:
    try:
        # if in notebook, do not use styles

        get_ipython  # type: ignore

        return {
            'title': '',
            'metavar': '',
            'description': '',
            'content': '',
            'option': '',
            'comment': '',
        }

    except NameError:
        return {
            'title': 'bold #ce93f9',
            'metavar': '#8be9fd',
            'description': '#b9f29f',
            'content': '#f1fa8c',
            'option': '#64aaaa',
            'comment': '#6272a4',
        }


def run_cli(
    raw_command: str | None = None,
    **toolcli_kwargs: typing.Any,
) -> None:

    import tempfile

    help_cache_dir = os.path.join(tempfile.gettempdir(), 'ctc', 'help_cache')

    # the goal of the below code would be to avoid having to import toolcli and
    # save 6 ms of startup time. but the problem with the below code is that
    # it produces a different cache key because the plugins have not been added
    #     if _is_root_help(raw_command):
    #         try:
    #             printed = _print_help_from_cache(
    #                 command_index, help_cache_dir
    #             )
    #             if printed:
    #                 return
    #         except Exception:
    #             pass

    styles = get_cli_styles()

    config: toolcli.CLIConfig = {
        #
        # metadata
        'base_command': 'ctc',
        'description': description,
        'version': ctc.__version__,
        'cd_dir_help': cd_dir_help,
        'cd_dir_getter': cd_dir_getter,
        'help_url_getter': help_url_getter,  # type: ignore
        'help_cache_dir': help_cache_dir,
        'help_subcommand_categories': help_subcommand_categories,
        'async_context_manager': cli_utils.AsyncContextManager,
        #
        'style_theme': styles,
        #
        # standard subcommands and standard args
        'include_standard_subcommands': True,
        'include_debug_arg': True,
        #
        # plugins
        'plugins': [toolsql_plugin.plugin],
        'extra_data': {
            'styles': styles,
        },
        'extra_data_getters': {
            'db_config': _db_config_getter,
            'db_schema': ('ctc.db', 'get_complete_prepared_schema'),  # type: ignore
        },
    }

    toolcli_kwargs = dict({'config': config}, **toolcli_kwargs)

    toolcli.run_cli(
        raw_command=raw_command,
        command_index=command_index,
        **toolcli_kwargs,
    )
