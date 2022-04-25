from __future__ import annotations

import re
import typing

from . import typedefs


def typehints_formatter(annotation, sphinx_config):
    """used for documentation of types by sphinx_autodoc_typehints"""
    output = str(annotation)
    matches = re.findall('[a-zA-Z_\.]+', output)
    for match in matches:
        if '.' in match:
            tokens = match.split('.')
            output = output.replace(match, tokens[-1])
    return output

