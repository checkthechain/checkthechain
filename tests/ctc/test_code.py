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
        relpaths = [os.path.relpath(path, root_path) for path in missing]
        print()
        print()
        print(len(missing), 'paths with missing future annotation import:')
        print()
        print('- ' + '\n- '.join(relpaths))
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
        relpaths = [os.path.relpath(path, root_path) for path in missing]
        print()
        print()
        print(len(missing), 'modules with missing __init__:')
        print()
        print(' '.join(relpaths))
    assert len(missing) == 0


def test_async_function_names():
    import importlib
    import inspect
    import pkgutil

    should_have_async_in_name = []
    should_not_have_async_in_name = []
    for importer, modname, ispkg in pkgutil.walk_packages(
        path=ctc.__path__,
        prefix="ctc.",
        onerror=lambda x: None,
    ):

        # skip files that run a lot of code
        if modname.endswith('__main__'):
            continue

        module = importlib.import_module(modname)
        for attr_name in dir(module):
            module_attr = getattr(module, attr_name)
            if hasattr(module_attr, '__call__'):
                named_as_async = attr_name.startswith(
                    'async'
                ) or attr_name.startswith('_async')
                if inspect.iscoroutinefunction(module_attr):
                    if not named_as_async:
                        should_have_async_in_name.append(modname + '.' + attr_name)
                else:
                    if named_as_async:
                        should_not_have_async_in_name.append(modname + '.' + attr_name)

    if len(should_have_async_in_name) > 0:
        message = 'names of these items should start with async_ or _async_:'
        for attr in should_have_async_in_name:
            message += '\n    - ' + attr
        raise Exception(message)
    if len(should_not_have_async_in_name) > 0:
        message = 'names of these items should not start with async_ or _async_:'
        for attr in should_not_have_async_in_name:
            message += '\n    - ' + attr
        raise Exception(message)
