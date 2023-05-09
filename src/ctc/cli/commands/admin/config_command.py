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
            description_style = None
            path_style = None
            key_style = None

        else:
            styles = cli.get_cli_styles()
            title_style = styles['title']
            chrome_style = styles['comment']
            key_style = styles['option']
            content_style = styles['content']
            description_style = styles['description']
            path_style = styles['metavar']

            path_style = path_style + ' bold'

        toolstr.print_text_box(
            'Config Summary', style=title_style, text_style=path_style
        )

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
        print()
        toolstr.print_header(
            'Environment Variables', style=title_style, text_style=path_style
        )
        for env_var in [
            ctc.config.config_path_env_var,
            ctc.config.provider_env_var,
            ctc.config.network_env_var,
            ctc.config.cache_env_var,
        ]:
            toolstr.print_bullet(
                key=env_var, value=os.environ.get(env_var), styles=styles
            )
        toolstr.print('(these are all optional)', style=chrome_style)

        print()
        print()
        toolstr.print_header(
            'Config Values', style=title_style, text_style=path_style
        )
        config = typing.cast(
            typing.Mapping[str, typing.Any], ctc.config.get_config()
        )

        for key in sorted(config.keys()):
            if key == 'cli_color_theme':
                toolstr.print(
                    toolstr.add_style('-', chrome_style),
                    toolstr.add_style(key, key_style)
                    + toolstr.add_style(':', chrome_style),
                )
                for subkey, subvalue in config[key].items():
                    toolstr.print(
                        '    ' + toolstr.add_style('-', chrome_style),
                        toolstr.add_style(subkey, key_style)
                        + toolstr.add_style(':', chrome_style),
                        toolstr.add_style(subvalue, subvalue),
                    )

            elif key == 'networks':
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
                labels = ['name', 'chain id', 'block_explorer']
                toolstr.print_table(
                    rows,
                    labels=labels,
                    indent=4,
                    label_style=title_style,
                    column_styles={
                        'name': description_style,
                        'chain id': content_style,
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
                labels = ['name', 'network', 'chain id', 'url']
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
                        elif label == 'chain id':
                            cell = config['networks'][provider['network']][
                                'chain_id'
                            ]
                        elif label == 'name':
                            cell = provider['name']
                        else:
                            cell = str(provider[label])
                        row.append(cell)
                    rows.append(row)
                toolstr.print_table(
                    rows,
                    labels=labels,
                    indent=4,
                    label_style=title_style,
                    border=chrome_style,
                    column_styles={
                        'name': description_style,
                        'network': description_style,
                        'url': path_style,
                        'chain id': content_style,
                    },
                    column_formats={
                        'chain id': {'commas': False},
                    },
                    sort_column=['chain id', 'name'],
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
                            toolstr.add_style(str(subkey), description_style)
                            + toolstr.add_style(':', chrome_style),
                        )
                        for subsubkey, subsubvalue in subvalue.items():
                            if key == 'db_configs' and subsubkey == 'path':
                                style = path_style
                            else:
                                style = description_style

                            toolstr.print(
                                toolstr.add_style('        -', chrome_style),
                                toolstr.add_style(
                                    str(subsubkey), description_style
                                )
                                + toolstr.add_style(':', chrome_style),
                                toolstr.add_style(str(subsubvalue), style),
                            )
                    else:
                        toolstr.print(
                            toolstr.add_style('    -', chrome_style),
                            toolstr.add_style(str(subkey), description_style)
                            + toolstr.add_style(':', chrome_style),
                            toolstr.add_style(str(subvalue), description_style),
                        )

            elif key == 'context_cache_rules':
                rules = config[key]
                rows = []
                for rule in rules:
                    row = []
                    row.append(rule.get('backend', ''))
                    row.append(rule.get('read', ''))
                    row.append(rule.get('write', ''))
                    filter = rule.get('filter')
                    if filter is None or len(filter) == 0:
                        scope = 'global'
                    else:
                        scope = ','.join(
                            (key + '=' + value) for key, value in filter.items()
                        )
                    row.append(scope)
                    rows.append(row)

                toolstr.print_bullet(
                    key='cache configuration', value='', key_style=key_style
                )
                labels = ['backend', 'read', 'write', 'scope']
                toolstr.print_table(
                    rows,
                    labels=labels,
                    indent=8,
                    label_style=title_style,
                    border=chrome_style,
                    column_styles={
                        'backend': path_style,
                        'read': description_style,
                        'write': description_style,
                        'scope': content_style,
                    },
                    add_row_index=True,
                )
                toolstr.print(
                    '(rules applied in order)',
                    style=chrome_style,
                    indent=8,
                )

            else:
                if key == 'data_dir':
                    style = path_style
                else:
                    style = description_style

                toolstr.print(
                    toolstr.add_style('-', chrome_style),
                    toolstr.add_style(key, key_style)
                    + toolstr.add_style(':', chrome_style),
                    toolstr.add_style(str(config[key]), style),
                )

