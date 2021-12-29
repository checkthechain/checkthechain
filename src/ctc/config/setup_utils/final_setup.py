import os

from .. import config_write
from .. import config_spec


def finalize_setup(create_new_config, config, config_path):

    print()
    print()
    print('## Final Steps')

    if create_new_config:
        print()
        config_write.write_config_file(
            config_data=config,
            path=config_path,
            overwrite='prompt',
        )

        print()
        print('Config file created at:', config_path)

    # remind user to set env var
    if os.environ.get(config_spec.config_path_env_var) != config_path:
        print()
        print(
            'Remember to set your',
            config_spec.config_path_env_var,
            'environment variable to',
            config_path,
        )
        print()
        print(
            'For example, if using bash you can add the following line to ~/.profile:'
        )
        print(
            'export',
            config_spec.config_path_env_var
            + '="'
            + config_path.replace('"', '\\"')
            + '"',
        )

    # print outro
    print()
    print('ctc setup complete')

