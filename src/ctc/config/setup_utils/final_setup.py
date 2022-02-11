import os

import toolcli

from .. import config_write
from .. import config_spec


def finalize_setup(create_new_config, config, config_path, styles):

    print()
    print()
    toolcli.print('## Final Steps', style=styles['header'])

    if create_new_config:
        config_write.write_config_file(
            config_data=config,
            path=config_path,
            overwrite='prompt',
            style=styles['question'],
        )

        print()
        toolcli.print(
            'Config file created at',
            toolcli.add_style(config_path, styles['path']),
        )

    # remind user to set env var
    if config_path != os.path.expanduser(config_spec.default_config_path):
        print()
        toolcli.print(
            'Remember to set your',
            toolcli.add_style(config_spec.config_path_env_var, styles['path']),
            'environment variable to',
            toolcli.add_style(config_path, styles['path']),
        )
        print()
        toolcli.print(
            'For example, if using bash you can add the following line to your'
            + toolcli.add_style('~/.profile:', styles['path'])
        )
        toolcli.print(
            toolcli.add_style('export', styles['quote']),
            toolcli.add_style(config_spec.config_path_env_var, styles['quote'])
            + toolcli.add_style('="', styles['quote'])
            + toolcli.add_style(
                config_path.replace('"', '\\"'), styles['quote']
            )
            + toolcli.add_style('"', styles['quote']),
        )

    else:
        print()
        toolcli.print('Using default config path ' + toolcli.add_style(config_path, styles['path']))

    # print outro
    print()
    print('ctc setup complete')

