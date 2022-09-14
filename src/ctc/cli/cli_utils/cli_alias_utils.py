from __future__ import annotations

import os
import sys
import typing

from ctc import cli


if typing.TYPE_CHECKING:

    from typing_extensions import TypedDict

    class AliasStatus(TypedDict):
        yes_aliases: typing.Sequence[str]
        no_aliases: typing.Sequence[str]
        yes_shells: typing.Sequence[str]
        no_shells: typing.Sequence[str]


aliases_content = """
#
# # ctc aliases
#

# compute commands
alias ascii="ctc ascii"
alias hex="ctc hex"
alias keccak="ctc keccak"
alias lower="ctc lower"

# data commands
alias abi="ctc abi"
alias address="ctc address"
alias block="ctc block"
alias blocks="ctc blocks"
alias bytecode="ctc bytecode"
alias call="ctc call"
alias calls="ctc calls"
alias dex="ctc dex"
alias erc20="ctc erc20"
alias eth="ctc eth"
alias gas="ctc gas"
alias int="ctc int"
alias rlp="ctc rlp"
alias tx="ctc tx"

# protocol commands
alias 4byte="ctc 4byte"
alias aave="ctc aave"
alias cg="ctc cg"
alias chainlink="ctc chainlink"
alias curve="ctc curve"
alias es="ctc etherscan"
alias ens="ctc ens"
alias fei="ctc fei"
alias gnosis="ctc gnosis"
alias llama="ctc llama"
alias rari="ctc rari"
alias uniswap="ctc uniswap"
alias yearn="ctc yearn"

#
# # end of ctc aliases
#
"""

alias_header = """#
# # ctc aliases
#
"""

alias_footer = """
#
# # end of ctc aliases
#"""


default_shell_paths = {
    '~/.bashrc': 'bash interactive',
    '~/.profile': 'bash login',
    '~/.zshrc': 'zsh',
}


#
# # ctc root command
#


def is_ctc_on_path() -> bool:
    import subprocess

    try:
        subprocess.check_output('bash -c "which ctc"', shell=True)
        return True
    except subprocess.CalledProcessError:
        return False


def create_root_ctc_alias() -> str:
    return 'alias ctc="' + sys.executable + '-m ctc"'


#
# # alias data
#


def print_raw_aliases() -> None:
    print(aliases_content)


def get_aliases() -> typing.Mapping[str, str]:
    aliases = {}
    for line in aliases_content.split('\n'):
        if line.startswith('alias'):
            index = line.index('=')
            alias = line[6:index]
            command = line[index + 1 :]
            aliases[alias] = command
    return aliases


#
# # alias reads
#


def detect_existing_shell_paths() -> typing.Mapping[str, bool]:
    return {
        path: os.path.isfile(os.path.expanduser(path))
        for path in default_shell_paths.keys()
    }


def does_file_contain_current_aliases(path: str) -> bool:

    path = os.path.expanduser(path)

    if not os.path.isfile(path):
        return False

    with open(path, 'r') as f:
        return aliases_content in f.read()


def does_file_contain_old_aliases(path: str) -> bool:

    path = os.path.expanduser(path)

    if not os.path.isfile(path):
        return False

    with open(path, 'r') as f:
        content = f.read()
        return (
            alias_header in content
            and alias_footer in content
            and content.index(alias_header) < content.index(alias_footer)
        )


#
# # alias writes
#


def install_aliases(
    paths: typing.Sequence[str] | None = None,
    *,
    confirm: bool = False,
    verbose: bool = True,
    headless: bool = False,
) -> None:

    import toolcli

    # autodetect path based on shell
    if paths is None:
        paths = [
            path
            for path, exists in detect_existing_shell_paths().items()
            if exists
        ]

    # check that aliases are not already on path
    global_confirm = confirm
    for path in paths:
        if does_file_contain_current_aliases(path):
            if verbose:
                print('File ' + path + ' already contains shell aliases')
            continue

        elif does_file_contain_old_aliases(path):
            if verbose:
                print('File ' + path + ' contains old aliases')
            if not confirm:
                confirm = toolcli.input_yes_or_no(
                    'Replace old aliases with new aliases? ',
                    headless=headless,
                )
                if not confirm:
                    continue
                else:
                    delete_aliases(path, confirm=confirm, headless=headless)

        # confirm
        if not confirm:
            print()

            answer = toolcli.input_yes_or_no(
                'Appending ctc aliases to ' + path + '\nContinue? ',
                headless=headless,
            )
            if not answer:
                continue

        # append to file
        path = os.path.expanduser(path)
        with open(path, 'a') as f:
            f.write('\n' + aliases_content)
            if verbose:
                print('Aliases added to', path)

        confirm = global_confirm


def delete_aliases(
    path: str,
    *,
    confirm: bool = False,
    headless: bool = False,
) -> None:

    import toolcli

    path = os.path.expanduser(path)

    with open(path, 'r') as f:
        content = f.read()

    if alias_header not in content or alias_footer not in content:
        raise Exception('could not detect aliases in file ' + str(path))
    header_index = content.index(alias_header)
    footer_index = content.index(alias_footer)
    end_clip_index = footer_index + len(alias_footer)
    clipped_content = content[header_index:end_clip_index]
    new_content = content[:header_index] + content[end_clip_index:]

    # ensure not deleting anything but comments, blanks, and aliases
    clipped_lines = clipped_content.split('\n')
    for line in clipped_lines:
        valid = line.startswith('#') or line.startswith('alias ') or line == ''
        if not valid:
            raise Exception(
                'could not delete aliases, there has been addititional content placed in the ctc section of the file'
            )

    if not confirm:
        answer = toolcli.input_yes_or_no(
            'Delete aliases from file ' + path + '?',
            headless=headless,
        )
        if not answer:
            raise Exception('not deleting aliases')

    with open(path, 'w') as f:
        f.write(new_content)


#
# # alias summary
#


def get_paths_alias_status(
    paths: typing.Sequence[str] | None = None,
) -> typing.Mapping[str, typing.Literal['old', 'current', 'missing']]:

    if paths is None:
        paths = list(default_shell_paths.keys())

    statuses: typing.MutableMapping[
        str, typing.Literal['old', 'current', 'missing']
    ] = {}
    for path in paths:
        if does_file_contain_current_aliases(path):
            statuses[path] = 'current'
        elif does_file_contain_old_aliases(path):
            statuses[path] = 'old'
        else:
            statuses[path] = 'missing'
    return statuses


def print_alias_status(include_title: bool = True) -> None:
    import toolstr

    styles = cli.get_cli_styles()
    if include_title:
        toolstr.print_text_box('ctc Aliases', style=styles['title'])
    print()
    print_paths_alias_status()
    print()
    print()
    print_aliases()
    print()
    toolstr.print(
        'typing each '
        + toolstr.add_style('alias', styles['description'])
        + ' is equivalent to typing each full '
        + toolstr.add_style('command', styles['option']),
        style=styles['comment'],
    )


def print_paths_alias_status(
    paths: typing.Sequence[str] | None = None,
) -> None:

    import toolstr

    if paths is None:
        paths = list(default_shell_paths.keys())
    paths_status = get_paths_alias_status(paths)

    rows = []
    for path, status in paths_status.items():
        shell = default_shell_paths.get(path, 'unknown shell')
        row = [path, shell, status]
        rows.append(row)
    labels = ['path', 'shell', 'status']
    styles = cli.get_cli_styles()
    toolstr.print_header('Alias Configuration', style=styles['title'])
    print()
    toolstr.print_table(
        rows,
        labels=labels,
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'path': styles['metavar'],
            'shell': styles['description'],
            'status': styles['description'],
        },
        indent=4,
    )

    not_current = any(status != 'current' for status in paths_status.values())
    if not_current:
        print()
        print()
        toolstr.print(
            '   install/update aliases using: '
            + toolstr.add_style('ctc aliases --install', styles['option']),
            style=styles['comment'],
        )


def print_aliases() -> None:
    import toolstr

    styles = cli.get_cli_styles()
    toolstr.print_header('Aliases', style=styles['title'])
    print()

    aliases = get_aliases()
    rows = []
    for alias, command in aliases.items():
        row = [alias, command.strip('"')]
        rows.append(row)
    labels = ['alias', 'command']
    toolstr.print_table(
        rows,
        labels=labels,
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'alias': styles['description'],
            'command': styles['option'],
        },
        indent=4,
    )
