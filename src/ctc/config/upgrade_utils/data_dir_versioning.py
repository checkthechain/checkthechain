from __future__ import annotations

import os
import typing

if typing.TYPE_CHECKING:

    from typing_extensions import TypedDict

    DirectoryTree = typing.Mapping[str, typing.Mapping[str, typing.Any]]

    class DataDirSpec(TypedDict, total=False):
        files: typing.Sequence[str]
        directory_tree: DirectoryTree

        # # for now, only specifies entries in root data dir
        # files: list[str]  # list of expected file paths
        # directories: list[str]  # list of expected directory paths
        # directory_subdirs: typing.Mapping[
        #     str, typing.Sequence[str]
        # ]  # list of items in each directory
        # move_items: typing.Mapping[str, str]

    DataSpecVersion = str


data_spec_order = [
    '0.2.0',
    '0.3.0',
    '0.3.1',
    '0.3.2',
    '0.3.3',
    '0.3.4',
    '0.3.5',
]

_0_3_0_spec: DataDirSpec = {
    'directory_tree': {
        'dbs': {},
        'logs': {'rpc': {}, 'db': {}},
        'evm': {},
    },
    'files': [
        './directory_version',
    ],
}

data_dir_specs: typing.Mapping[DataSpecVersion, DataDirSpec] = {
    '0.2.0': {
        'files': [],
        'directory_tree': {},
    },
    '0.3.0': _0_3_0_spec,
    '0.3.1': _0_3_0_spec,
    '0.3.2': _0_3_0_spec,
    '0.3.3': _0_3_0_spec,
    '0.3.4': _0_3_0_spec,
    '0.3.5': _0_3_0_spec,
}


def initialize_data_subdirs(data_dir: str, *, version: str) -> None:
    if version in data_spec_order:
        data_dir_spec = data_dir_specs[version]
    else:
        raise Exception('invalid version: ' + str(version))

    directory_tree = data_dir_spec['directory_tree']
    tree_paths = _flatten_tree(directory_tree)
    for tree_path in tree_paths:
        os.makedirs(os.path.join(data_dir, tree_path), exist_ok=True)


def _flatten_tree(directory_tree: DirectoryTree) -> typing.Sequence[str]:
    """return depth-first flattening of nested dict filesystem tree"""
    flat = []
    for dirname, subdirs in directory_tree.items():
        flat.append(dirname)
        if len(subdirs) > 0:
            for subdir in _flatten_tree(subdirs):
                flat.append(os.path.join(dirname, subdir))
    return flat


# def initialize_data_subdirs(data_dir: str, *, version: DataSpecVersion) -> None:
#     data_dir_spec = data_dir_specs[version]

#     for dirname in data_dir_spec.get('directories', []):
#         path = os.path.join(data_dir, dirname)
#         if not os.path.isdir(path):
#             print('creating directory:', path)
#             os.makedirs(path, exist_ok=True)

#     for dirname in data_dir_spec.get('directory_subdirs', []):
#         for subdirname in data_dir_spec['directory_subdirs'][dirname]:
#             path = os.path.join(data_dir, dirname, subdirname)
#             if not os.path.isdir(path):
#                 print('creating directory:', path)
#                 os.makedirs(path, exist_ok=True)


# def get_data_dir_version(data_dir: str | None = None) -> DataSpecVersion:
#     if data_dir is None:
#         data_dir = config.get_data_dir()

#     version_file = os.path.join(data_dir, 'directory_version')

#     if not os.path.isfile(version_file):
#         return '0.2.0'
#     else:
#         with open(version_file, 'r') as f:
#             version = f.read()
#         if version in data_spec_order:
#             return typing.cast(DataSpecVersion, version)
#         else:
#             raise Exception('unknown data_spec_version: ' + str(version))


# def fully_migrate_data_dir(data_dir: str | None = None) -> None:

#     if data_dir is None:
#         data_dir = config.get_data_dir()

#     # detect current version
#     current_version = get_data_dir_version()
#     latest_version = data_spec_order[-1]
#     if current_version == latest_version:
#         print('data_dir already fully migrated')
#         return

#     # gather all migrate functions, use None if no migration necessary
#     migrate_functions = {
#         '0.3.0': migrate_data_dir__0_2_0__to__0_3_0,
#         '0.3.1': None,
#     }

#     # perform each upgrade function sequentially
#     index = data_spec_order.index(current_version)
#     steps = data_spec_order[index + 1:]
#     for step in steps:
#         f = migrate_functions[step]
#         if f is not None:
#             f(data_dir=data_dir)


# def migrate_data_dir__0_2_0__to__0_3_0(
#     data_dir: str,
#     *,
#     delete_old_data: bool = True,
#     confirm_delete: bool = False,
# ) -> None:

#     data_dir_spec = data_dir_specs['0.3.0']

#     # create version file
#     version_file = os.path.join(data_dir, 'directory_version')
#     print('creating new version indicator file:', version_file)
#     with open(version_file, 'w') as f:
#         f.write('0.3.0')

#     # create new directories
#     for relpath in data_dir_spec['directories']:
#         dirpath = os.path.join(data_dir, relpath)
#         print('creating directory:', dirpath)
#         os.makedirs(dirpath, exist_ok=True)

#     # migrate data (the only old data that is migrated is events)
#     print()
#     for old_item, new_item in data_dir_spec['move_items'].items():
#         old_path = os.path.join(data_dir, old_item)
#         new_path = os.path.join(data_dir, new_item)
#         if os.path.exists(old_path):
#             print('moving', old_item, 'to', new_item)
#             new_parent = os.path.dirname(new_path)
#             os.makedirs(new_parent, exist_ok=True)
#             shutil.move(old_path, new_path)

#     # delete old files
#     if delete_old_data:
#         to_delete = []
#         for item in os.listdir(data_dir):
#             if (
#                 item not in data_dir_spec['directories']
#                 and item not in data_dir_spec['files']
#             ):
#                 to_delete.append(item)
#             elif (
#                 item in data_dir_spec['directories']
#                 and item in data_dir_spec['directory_subdirs']
#             ):
#                 directory_subdirs = data_dir_spec['directory_subdirs'][item]
#                 for subitem in os.listdir(os.path.join(data_dir, item)):
#                     if subitem not in directory_subdirs:
#                         to_delete.append(os.path.join(item, subitem))
#         if len(to_delete) > 0:
#             if not confirm_delete:
#                 print()
#                 print(
#                     'the following files and directories are not used in ctc 0.3.0:'
#                 )
#                 for item in sorted(to_delete):
#                     print('-', item)
#                 print()
#                 if not toolcli.input_yes_or_no('delete these items? '):
#                     raise Exception(
#                         'migration unfinished, must delete old files'
#                     )

#             for path in to_delete:
#                 path = os.path.join(data_dir, path)
#                 if os.path.isfile(path) or os.path.islink(path):
#                     os.remove(path)
#                 elif os.path.isdir(path):
#                     shutil.rmtree(path)
#                 else:
#                     raise Exception('cannot process path: ' + str(path))

#     print('data migration complete, now using the 0.3.0 data schema')
