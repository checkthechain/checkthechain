from __future__ import annotations

import os
import sys
import typing

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
alias erc20="ctc erc20"
alias eth="ctc eth"
alias gas="ctc gas"
alias tx="ctc tx"

# protocol commands
alias 4byte="ctc 4byte"
alias cg="ctc cg"
alias chainlink="ctc chainlink"
alias curve="ctc curve"
alias ens="ctc ens"
alias fei="ctc fei"
alias gnosis="ctc gnosis"
alias rari="ctc rari"
alias uniswap="ctc uniswap"

#
# # end of ctc aliases
#
"""


def is_ctc_on_path() -> bool:
    import subprocess

    try:
        subprocess.check_output('bash -c "which ctc"', shell=True)
        return True
    except subprocess.CalledProcessError:
        return False


def create_root_ctc_alias() -> str:
    return 'alias ctc="' + sys.executable + '-m ctc"'


def print_aliases() -> None:
    print(aliases_content)


def get_alias_list() -> typing.Sequence[str]:
    aliases = []
    for line in aliases_content.split('\n'):
        if line.startswith('alias'):
            index = line.index('=')
            alias = line[6:index]
            aliases.append(alias)
    return aliases


def append_aliases_to_shell_configs(
    paths: typing.Sequence[str] | None = None,
    *,
    confirm: bool = False,
    verbose: bool = True,
) -> None:

    # autodetect path based on shell
    if paths is None:
        paths = detect_shell_config_paths(verbose=verbose)

    # check that aliases are not already on path
    for path in paths:
        if does_file_contain_aliases(path):
            if verbose:
                print('file ' + path + ' already contains shell aliases')
            continue

        # confirm
        if not confirm:
            print()
            import toolcli
            answer = toolcli.input_yes_or_no(
                'Appending ctc aliases to ' + path + '\nContinue? '
            )
            if not answer:
                continue

        # append to file
        with open(path, 'a') as f:
            f.write('\n' + aliases_content)
            if verbose:
                print('aliases added to', path)


def detect_shell_config_paths(verbose: bool = True) -> typing.Sequence[str]:
    """by default, returns ~/.bashrc and if it exists, ~/.zshrc

    see https://askubuntu.com/a/606882 for bash configuration summary
    """

    # gather paths
    paths = [os.path.expanduser('~/.bashrc')]
    zsh_path = os.path.expanduser('~/.zshrc')
    if os.path.isfile(zsh_path):
        paths.append(zsh_path)

    # print summary
    if verbose:
        print('Detected the following shell config paths:')
        for path in paths:
            print('-', path)

    return paths


def does_file_contain_aliases(path: str) -> bool:
    if not os.path.isfile(path):
        return False
    with open(path, 'r') as f:
        return aliases_content in f.read()


def get_alias_status(paths: typing.Sequence[str] | None = None) -> AliasStatus:

    if paths is None:
        paths = detect_shell_config_paths(verbose=False)

    yes_aliases = []
    no_aliases = []
    yes_shells = []
    no_shells = []

    for path in paths:
        if path.endswith('.bashrc'):
            shell = 'bash'
        elif path.endswith('.zshrc'):
            shell = 'zsh'
        else:
            shell = 'unknown shell'

        if does_file_contain_aliases(path):
            yes_aliases.append(path)
            yes_shells.append(shell)
        else:
            no_aliases.append(path)
            no_shells.append(shell)

    return {
        'yes_aliases': yes_aliases,
        'no_aliases': no_aliases,
        'yes_shells': yes_shells,
        'no_shells': no_shells,
    }


def print_alias_status(
    alias_status: AliasStatus | None = None,
    styles: typing.Mapping[str, str] | None = None,
) -> None:
    if styles is not None:
        import toolcli

    if alias_status is None:
        alias_status = get_alias_status()

    yes_aliases = alias_status['yes_aliases']
    no_aliases = alias_status['no_aliases']
    yes_shells = alias_status['yes_shells']
    no_shells = alias_status['no_shells']

    if len(no_aliases) > 0:
        print('These shells do not have ctc aliases installed:')
        for shell, path in zip(no_shells, no_aliases):
            if styles is not None:
                styled_shell = toolcli.add_style(shell, style=styles['command'])
                styled_path = toolcli.add_style(path, style=styles['path'])
                toolcli.print('-', styled_shell, '(' + styled_path + ')')
            else:
                print('-', shell, '(' + path + ')')
    if len(yes_aliases) > 0 and len(no_aliases) > 0:
        print()
    if len(yes_aliases) > 0:
        print('These shells already have ctc aliases installed:')
        for shell, path in zip(yes_shells, yes_aliases):
            if styles is not None:
                styled_shell = toolcli.add_style(shell, style=styles['command'])
                styled_path = toolcli.add_style(path, style=styles['path'])
                toolcli.print('-', styled_shell, '(' + styled_path + ')')
            else:
                print('-', shell, '(' + path + ')')
