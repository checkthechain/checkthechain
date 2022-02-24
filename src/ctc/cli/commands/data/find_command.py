import tooltable
from ctc import directory


def get_command_spec():
    return {
        'f': async_find_command,
        'args': [
            {'name': 'query'},
        ]
    }


async def async_find_command(query):
    try:
        result = directory.get_erc20_metadata(symbol=query)
        row = []
        headers = ['symbol', 'decimals', 'address']
        for key in headers:
            row.append(result[key])
        rows = [row]
        tooltable.print_table(rows=rows, headers=headers)
    except LookupError:
        print('could not find anything')

