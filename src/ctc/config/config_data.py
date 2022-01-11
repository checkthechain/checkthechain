import filecmp
import os
import shutil

import toolcli

import ctc


def get_default_data_dir() -> str:
    return os.path.abspath(os.path.join(ctc.__path__[0], 'default_data'))


def is_data_root_initialized(data_root_path: str) -> bool:
    """a data root is considered initialized if it contains all default data"""

    data_root_path = os.path.abspath(data_root_path)
    default_data_dir = get_default_data_dir()

    for root, subdirs, files in os.walk(default_data_dir):

        if root == default_data_dir:
            check_root = data_root_path
        else:
            root_relpath = os.path.relpath(root, default_data_dir)
            check_root = os.path.join(data_root_path, root_relpath)

        for subdir in subdirs:
            subdir_path = os.path.join(check_root, subdir)
            if not os.path.isdir(subdir_path):
                return False
        for file in files:
            default_data_file_path = os.path.join(root, file)
            file_path = os.path.join(check_root, file)
            if not os.path.isfile(file_path) or not filecmp.cmp(
                file_path, default_data_file_path
            ):
                return False

    return True


def initialize_data_root(
    path: str, confirm: bool = False, raise_if_unconfirmed: bool = True
) -> bool:

    default_data_dir = get_default_data_dir()

    # validate directory name
    if os.path.splitext(path)[-1] != '':
        raise Exception('must use a directory path, not a file path')

    print()
    print('Will use data root:', path)
    if not os.path.isdir(path):
        if not confirm:
            print()
            answer = toolcli.input_yes_or_no(
                'Directory does not exist. Create it?', default='yes'
            )
            if not answer:
                if raise_if_unconfirmed:
                    raise Exception('must create directory')
                else:
                    return False

    else:
        overwritten = []
        new_files = []
        unchanged_files = []
        for root, subdirs, files in os.walk(default_data_dir):

            if root == default_data_dir:
                check_root = path
            else:
                root_relpath = os.path.relpath(root, default_data_dir)
                check_root = os.path.join(path, root_relpath)

            # root_relpath = os.path.relpath(root, default_data_dir)
            # check_root = os.path.join(path, root_relpath)
            for file in files:
                filepath = os.path.join(check_root, file)
                if os.path.isfile(filepath):
                    with open(filepath, 'r') as f:
                        old_file_data = f.read()
                    with open(os.path.join(root, file), 'r') as f:
                        new_file_data = f.read()
                    if old_file_data == new_file_data:
                        unchanged_files.append(filepath)
                    else:
                        overwritten.append(filepath)
                else:
                    new_files.append(filepath)

        if len(new_files) > 0:
            print()
            print('Writing', len(new_files), 'new files')
            for new_file in new_files:
                print('-', new_file)

        if len(overwritten) > 0:
            print()
            print('Will overwrite the following files:')
            for filepath in overwritten:
                print('-', filepath)
            print()
            answer = toolcli.input_yes_or_no(
                'Continue? ', default='yes', default_prefix='(default = '
            )
            if not answer:
                if raise_if_unconfirmed:
                    raise Exception('Must overwrite files to continue')
                else:
                    return False

    # create directory
    shutil.copytree(default_data_dir, path, dirs_exist_ok=True)
    return True

