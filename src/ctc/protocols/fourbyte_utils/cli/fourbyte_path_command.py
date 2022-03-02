import os

import toolstr

from ctc.protocols import fourbyte_utils


def get_command_spec():
    return {
        'f': fourbyte_path_command,
        'help': 'show paths of local 4byte database',
    }


def fourbyte_path_command():
    function_path = fourbyte_utils.get_default_path('function_signatures')
    event_path = fourbyte_utils.get_default_path('event_signatures')

    if os.path.isfile(function_path):
        function_exists = '[EXISTS]'
    else:
        function_exists = '[DOES NOT EXIST]'
    if os.path.isfile(event_path):
        event_exists = '[EXISTS]'
    else:
        event_exists = '[DOES NOT EXIST]'

    toolstr.print_text_box('4byte paths')
    print('- directory:', os.path.dirname(function_path))
    print('-', function_exists, 'function signatures:', function_path)
    print('-', event_exists, 'event signatures:', event_path)

