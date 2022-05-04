import os

import ctc


def test_code_imports_future_annotations():

    phrase = 'from __future__ import annotations'
    root_path = ctc.__path__[0]

    missing = []
    for root, dirnames, filenames in os.walk(root_path):
        for filename in filenames:
            if not filename.startswith('__') and filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                with open(filepath, 'r') as f:
                    content = f.read()
                if phrase not in content:
                    missing.append(filepath)

    if len(missing) > 0:
        relpaths = [
            os.path.relpath(path, root_path)
            for path in missing
        ]
        print()
        print()
        print(len(missing), 'paths with missing future annotation import:')
        print()
        print(' '.join(relpaths))
    assert len(missing) == 0


def test_every_module_has_init_file():
    root_path = ctc.__path__[0]

    missing = []
    for root, dirnames, filenames in os.walk(root_path):
        needs_init = any(filename.endswith('.py') for filename in filenames)

        if needs_init:
            if '__init__.py' not in os.listdir(root):
                missing.append(root)

    if len(missing) > 0:
        relpaths = [
            os.path.relpath(path, root_path)
            for path in missing
        ]
        print()
        print()
        print(len(missing), 'modules with missing __init__:')
        print()
        print(' '.join(relpaths))
    assert len(missing) == 0

