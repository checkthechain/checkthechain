from __future__ import annotations

import os
import typing

import toolcli


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
    paths: typing.Sequence[str] | None = None, confirm: bool = False
) -> None:

    # autodetect path based on shell
    if paths is None:
        paths = detect_shell_config_paths()

    # check that aliases are not already on path
    for path in paths:
        if os.path.isfile(path):
            with open(path, 'r') as f:
                file_content = f.read()
            if aliases_content in file_content:
                print('file already contains shell aliases')
                continue

        # confirm
        if not confirm:
            print()
            answer = toolcli.input_yes_or_no(
                'Appending ctc aliases to ' + path + '\nContinue? '
            )
            if not answer:
                continue

        # append to file
        with open(path, 'a') as f:
            f.write('\n' + aliases_content)
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
