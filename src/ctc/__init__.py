"""ctc is a tool for collecting and processing historical EVM data"""

from .evm import *


__version__ = '0.3.0'


def _clean_package_imports() -> None:
    """remove deep nested modules from ctc namespace"""

    import sys

    ctc = sys.modules['ctc']
    moduletype = type(ctc)
    delattr(ctc, 'annotations')
    for key, value in tuple(vars(ctc).items()):
        if isinstance(value, moduletype):
            name = value.__name__
            if not name.startswith('ctc') or name.count('.') > 1:
                delattr(ctc, key)


_clean_package_imports()
