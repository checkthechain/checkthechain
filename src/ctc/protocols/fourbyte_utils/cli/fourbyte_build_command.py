from ctc.protocols import fourbyte_utils


def get_command_spec():
    return {
        'f': async_fourbyte_build_command,
        'help': 'build local copy of 4byte database',
        'args': [
            {
                'name': 'datatype',
                'choices': ['functions', 'events'],
                'nargs': '?',
                'help': '"functions" or "events", omit to build database of both',
            },
        ],
    }


async def async_fourbyte_build_command(datatype):
    if datatype is None:
        datatypes = ['functions', 'events']
    else:
        datatypes = [datatype]

    print('Building local copy of 4byte database...')

    if 'functions' in datatypes:
        if not fourbyte_utils.local_function_signatures_exist():
            print()
            print('(building function signatures from scratch, may take awhile')

        print()
        await fourbyte_utils.async_build_function_signatures_dataset()

    if 'events' in datatypes:
        if not fourbyte_utils.local_event_signatures_exist():
            print()
            print('(building event signatures from scratch, may take awhile')

        print()
        await fourbyte_utils.async_build_event_signatures_dataset()

    print()
    print('local 4byte database up to date')

