from ctc.protocols import chainlink_utils


def get_command_spec():
    return {
        'f': chainlink_command,
        'options': [
            {'name': 'feed'},
        ]
    }


def chainlink_command(feed, **kwargs):
    chainlink_utils.summarize_feed(feed=feed)

