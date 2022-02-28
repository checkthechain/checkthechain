from ctc import config


def get_command_spec():
    return {
        'f': setup_command,
        'help': 'run ctc setup wizard',
    }


def setup_command():
    config.setup_ctc()

