"""ctc is a tool for collecting and processing historical EVM data"""

from __future__ import annotations


__version__ = '0.3.0b1'


def get_version_tuple() -> tuple[int, int, int]:

    # remove alpha, beta, and release candidate tokens
    version_str = __version__
    for token in ['a', 'b', 'rc']:
        if token in version_str:
            version_str = version_str[version_str.index(token)]
            break

    tokens = version_str.split('.')
    return (int(tokens[0]), int(tokens[1]), int(tokens[2]))
