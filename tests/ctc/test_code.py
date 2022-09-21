import os
import types

import ctc


def test_ctc_functions_have_docstrings():
    functiontype = type(test_ctc_functions_have_docstrings)

    functions_without_docstrings = []
    for key, value in vars(ctc).items():
        if isinstance(value, functiontype):
            docstring = value.__doc__
            if docstring is None or docstring == '':
                functions_without_docstrings.append(value.__name__)
                continue
            lines = docstring.split('\n')
            if lines[0] == '':
                functions_without_docstrings.append(value.__name__)

    if len(functions_without_docstrings) > 0:
        raise Exception(
            'some functions do not have docstrings:\n    '
            + '\n    '.join(functions_without_docstrings)
        )


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


def test_function_names():
    import importlib
    import inspect
    import pkgutil

    should_have_async_in_name = []
    should_not_have_async_in_name = []
    async_exceptions = [
        '__aenter__',
        '__aexit__',
    ]

    should_use_by_block = []
    by_block_exceptions = [
        'bin_by_blocks',
    ]

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
                check_function_name(
                    module_attr=module_attr,
                    attr_name=attr_name,
                    modname=modname,
                    should_have_async_in_name=should_have_async_in_name,
                    should_not_have_async_in_name=should_not_have_async_in_name,
                    should_use_by_block=should_use_by_block,
                    async_exceptions=async_exceptions,
                    by_block_exceptions=by_block_exceptions,
                )

            # check methods of classes
            if (
                isinstance(module_attr, type)
                and module_attr.__module__ == modname
            ):
                methods = inspect.getmembers(
                    module_attr, predicate=inspect.ismethod
                )
                for method_name, method in methods:
                    check_function_name(
                        module_attr=method,
                        attr_name=method_name,
                        modname=modname + '.' + attr_name,
                        should_have_async_in_name=should_have_async_in_name,
                        should_not_have_async_in_name=should_not_have_async_in_name,
                        should_use_by_block=should_use_by_block,
                        async_exceptions=async_exceptions,
                        by_block_exceptions=by_block_exceptions,
                    )

    if len(should_have_async_in_name) > 0:
        message = 'names of these items should start with async_ or _async_:'
        for attr in sorted(should_have_async_in_name):
            message += '\n    - ' + attr
        raise Exception(message)
    if len(should_not_have_async_in_name) > 0:
        message = (
            'names of these items should not start with async_ or _async_:'
        )
        for attr in sorted(should_not_have_async_in_name):
            message += '\n    - ' + attr
        raise Exception(message)
    if len(should_use_by_block) > 0:
        message = (
            'functions should use by_block instead of per_block or by_blocks'
        )
        for attr in sorted(should_use_by_block):
            message += '\n    - ' + attr
        raise Exception(message)


def check_function_name(
    module_attr,
    attr_name,
    modname,
    should_have_async_in_name,
    should_not_have_async_in_name,
    should_use_by_block,
    async_exceptions,
    by_block_exceptions,
):
    import inspect

    named_as_async = attr_name.startswith('async') or attr_name.startswith(
        '_async'
    )
    if inspect.iscoroutinefunction(module_attr):
        if not named_as_async and attr_name not in async_exceptions:
            should_have_async_in_name.append(modname + '.' + attr_name)
    else:
        if named_as_async and attr_name not in async_exceptions:
            should_not_have_async_in_name.append(modname + '.' + attr_name)

    if 'per_block' in attr_name or 'by_blocks' in attr_name:
        if attr_name not in by_block_exceptions:
            should_use_by_block.append(modname + '.' + attr_name)


def iterate_package_functions(prefix):
    import importlib
    import pkgutil

    functions = {}
    function_to_name = {}

    for importer, modname, ispkg in pkgutil.walk_packages(
        path=ctc.__path__,
        prefix=prefix,
        onerror=lambda x: None,
    ):

        # skip files that run a lot of code
        if modname.endswith('__main__'):
            continue

        module = importlib.import_module(modname)
        for attr_name in dir(module):
            module_attr = getattr(module, attr_name)
            if isinstance(module_attr, types.FunctionType):

                function_data = {
                    'module_name': modname,
                    'function_name': attr_name,
                    'function': module_attr,
                    'module': module,
                }
                name = modname + '.' + attr_name

                if module_attr not in function_to_name:
                    functions[name] = function_data
                    function_to_name[module_attr] = name
                else:
                    # use longest valid name for function
                    other_name = function_to_name[module_attr]
                    if len(name) > len(other_name):
                        del functions[other_name]
                        functions[name] = function_data
                        function_to_name[module_attr] = name

    return functions


def test_max_positional_args():
    import inspect

    max_positional_args = 2

    too_many = []
    for function_name, function_data in iterate_package_functions(
        'ctc.'
    ).items():
        argspec = inspect.getfullargspec(function_data['function'])
        if len(argspec.args) > max_positional_args:
            too_many.append(function_name)

    for class_name, class_data in iterate_package_classes('ctc.').items():
        for method_name, method in class_data['methods']:
            argspec = inspect.getfullargspec(method)
            if len(argspec.args) > max_positional_args + 1:
                too_many.append(class_name + '.' + method_name)

    if len(too_many) > 0:
        message = (
            'functions should take no more than '
            + str(max_positional_args)
            + ' positional args, use `*` to convert to keyword-only arguments'
        )
        for item in too_many:
            message += '\n- ' + item
        message += '\n' + str(len(too_many)) + ' violations'
        message += '\n\nuse `*` to convert to keyword-only arguments'
        raise Exception(message)


def iterate_package_classes(prefix, include_methods=True):
    import importlib
    import inspect
    import pkgutil

    classes = {}
    classes_to_name = {}

    for importer, modname, ispkg in pkgutil.walk_packages(
        path=ctc.__path__,
        prefix=prefix,
        onerror=lambda x: None,
    ):

        # skip files that run a lot of code
        if modname.endswith('__main__'):
            continue

        module = importlib.import_module(modname)
        for attr_name in dir(module):
            module_attr = getattr(module, attr_name)
            if (
                isinstance(module_attr, type)
                and module_attr.__module__ == module.__name__
            ):

                class_data = {
                    'module_name': modname,
                    'class_name': attr_name,
                    'class': module_attr,
                    'module': module,
                }

                if include_methods:
                    class_data['methods'] = inspect.getmembers(
                        module_attr,
                        predicate=inspect.ismethod,
                    )

                name = modname + '.' + attr_name
                if module_attr not in classes_to_name:
                    classes[name] = class_data
                    classes_to_name[module_attr] = name
                else:
                    # use longest valid name for function
                    other_name = classes_to_name[module_attr]
                    if len(name) > len(other_name):
                        del classes[other_name]
                        classes[name] = class_data
                        classes_to_name[module_attr] = name

    return classes
