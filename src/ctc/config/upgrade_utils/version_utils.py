from __future__ import annotations


def get_stable_version(version_str: str) -> str:
    if version_str.count('.') != 2:
        raise Exception('invalid version spec')
    major, minor, bugfix = version_str.split('.')
    if not major.isnumeric() or not minor.isnumeric():
        raise Exception('invalid version spec')
    for i in range(len(bugfix)):
        if not bugfix[i].isnumeric():
            stable_bugfix = bugfix[:i]
            break
    else:
        stable_bugfix = bugfix
    if len(stable_bugfix) == 0:
        raise Exception('invalid version spec')
    return '.'.join([major, minor, stable_bugfix])
