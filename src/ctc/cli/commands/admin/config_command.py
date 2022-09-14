from __future__ import annotations

import os
import typing

import toolcli
import toolstr

from ctc import cli
import ctc.config


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': config_command,
        'help': 'print current config information',
        'args': [
            {
                'name': '--reveal',
                'action': 'store_true',
                'help': 'show sensitive information in config',
            },
            {
                'name': '--json',
                'help': 'output config as json',
                'dest': 'as_json',
                'action': 'store_true',
            },
            {
                'name': '--no-color',
                'action': 'store_true',
                'help': 'do not use color',
            },
        ],
        'examples': [
            '',
            '--reveal',
            '--json',
        ],
    }


def config_command(*, reveal: bool, as_json: bool, no_color: bool) -> None:

    env_var = ctc.config.config_path_env_var

    if as_json:
        config: typing.Mapping[str, typing.Any] = ctc.config.get_config()

        if no_color:
            import json

            print(json.dumps(config, indent=4, sort_keys=True))
        else:
            import rich

            rich.print(config)

    else:

        # get styles
        if no_color:
            title_style = None
            chrome_style = None
            content_style = None
            path_style = None
            key_style = None

        else:
            styles = cli.get_cli_styles()
            title_style = styles['title']
            chrome_style = styles['comment']
            key_style = styles['option']
            content_style = styles['description']
            path_style = styles['metavar']

            path_style = path_style + ' bold'

        toolstr.print('# Config Summary', style=title_style)

        # print config path
        env_var_value = os.environ.get(env_var)
        config_path = ctc.config.get_config_path(raise_if_dne=False)

        styled_path = toolstr.add_style(config_path, path_style)
        if env_var_value in (None, ''):
            toolstr.print(
                toolstr.add_style('using default config path: ', key_style)
                + styled_path
            )
        else:
            toolstr.print(
                toolstr.add_style(
                    'using config path in CTC_CONFIG_PATH:', key_style
                ),
                styled_path,
            )

        print()
        toolstr.print('## Config Values', style=title_style)
        config = typing.cast(
            typing.Mapping[str, typing.Any], ctc.config.get_config()
        )
        for key in sorted(config.keys()):

            if key == 'networks':
                print()
                toolstr.print(
                    toolstr.add_style('-', chrome_style),
                    toolstr.add_style(key, key_style)
                    + toolstr.add_style(':', chrome_style),
                )
                rows = []
                for chain_id, network_metadata in config[key].items():
                    row = [
                        network_metadata['name'],
                        str(network_metadata['chain_id']),
                        network_metadata['block_explorer'],
                    ]
                    rows.append(row)
                labels = ['name', 'chain_id', 'block_explorer']
                toolstr.print_table(
                    rows,
                    labels=labels,
                    indent=4,
                    label_style=title_style,
                    column_styles={
                        'name': content_style,
                        'chain_id': content_style,
                        'block_explorer': path_style,
                    },
                    border=chrome_style,
                )
                print()

            elif key == 'providers':
                toolstr.print(
                    toolstr.add_style('-', chrome_style),
                    toolstr.add_style(key, key_style)
                    + toolstr.add_style(':', chrome_style),
                )
                if len(config[key]) == 0:
                    continue
                labels = ['name', 'network', 'url']
                rows = []
                for provider in config[key].values():
                    row = []
                    for label in labels:
                        if label == 'url' and not reveal:
                            cell = '*' * 8
                        elif label == 'network':
                            cell = config['networks'][provider['network']][
                                'name'
                            ]
                        else:
                            cell = str(provider[label])
                        row.append(cell)
                    rows.append(row)
                toolstr.print_table(
                    rows,
                    labels=labels,
                    indent=4,
                    label_style=title_style,
                    column_styles={
                        'name': content_style,
                        'network': content_style,
                        'url': path_style,
                    },
                    border=chrome_style,
                )

                if not reveal:
                    print()
                    toolstr.print(
                        toolstr.add_style('    (use ', chrome_style)
                        + toolstr.add_style('--reveal', key_style)
                        + toolstr.add_style(
                            ' to reveal sensitive provider information)',
                            chrome_style,
                        )
                    )

            elif isinstance(config[key], dict) and len(config[key]) > 0:
                toolstr.print(
                    toolstr.add_style('-', chrome_style),
                    toolstr.add_style(key, key_style)
                    + toolstr.add_style(':', chrome_style),
                )
                for subkey, subvalue in config[key].items():
                    if isinstance(subvalue, dict) and len(subvalue) > 0:
                        toolstr.print(
                            toolstr.add_style('    -', chrome_style),
                            toolstr.add_style(str(subkey), content_style)
                            + toolstr.add_style(':', chrome_style),
                        )
                        for subsubkey, subsubvalue in subvalue.items():

                            if key == 'db_configs' and subsubkey == 'path':
                                style = path_style
                            else:
                                style = content_style

                            toolstr.print(
                                toolstr.add_style('        -', chrome_style),
                                toolstr.add_style(str(subsubkey), content_style)
                                + toolstr.add_style(':', chrome_style),
                                toolstr.add_style(subsubvalue, style),
                            )
                    else:
                        toolstr.print(
                            toolstr.add_style('    -', chrome_style),
                            toolstr.add_style(str(subkey), content_style)
                            + toolstr.add_style(':', chrome_style),
                            toolstr.add_style(str(subvalue), content_style),
                        )
            else:
                if key == 'data_dir':
                    style = path_style
                else:
                    style = content_style

                toolstr.print(
                    toolstr.add_style('-', chrome_style),
                    toolstr.add_style(key, key_style)
                    + toolstr.add_style(':', chrome_style),
                    toolstr.add_style(str(config[key]), style),
                )
