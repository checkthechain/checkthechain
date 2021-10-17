import os

from . import dune_spec
from fei import config_utils


def get_dune_root():
    data_root = config_utils.get_config()['data_root']
    dune_root = os.path.join(data_root, 'dune')
    return dune_root


def get_dune_path(**kwargs):

    if kwargs.get('event_name') is not None:
        subpath = dune_spec.path_templates['events'].format(**kwargs)
    elif kwargs.get('function_name') is not None:
        subpath = dune_spec.path_templates['calls'].format(**kwargs)
    else:
        raise Exception('unknown data type')

    path = os.path.join(get_dune_root(), subpath)

    return path


def list_dune_paths(datatype, dune_view, group_name, **filters):
    dune_root = get_dune_root()
    group_dir = os.path.join(dune_root, dune_view, group_name)
    paths = [
        os.path.join(group_dir, filename) for filename in os.listdir(group_dir)
    ]

    if filters is not None:
        parsed_kwargs = {
            'datatype': datatype,
            'dune_view': dune_view,
            'group_name': group_name,
        }
        parsed_kwargs.update(filters)
        filtered_paths = []
        for path in paths:
            parsed_path = parse_dune_path(path, **parsed_kwargs)
            for filter_key, filter_value in filters.items():
                if parsed_path.get(filter_key) != filter_value:
                    break
            else:
                filtered_paths.append(path)
        paths = filtered_paths

    return paths


def parse_dune_path(path, datatype, **extra_keys):
    template = dune_spec.path_templates[datatype]
    template_filename = os.path.basename(os.path.splitext(template)[0])
    template_pieces = template_filename.split('__')
    filename_pieces = os.path.basename(os.path.splitext(path)[0]).split('__')
    assert len(template_pieces) == len(filename_pieces)

    keys = {}
    for template_piece, filename_piece in zip(template_pieces, filename_pieces):
        if template_piece.startswith('{'):

            key = template_piece[1:-1]

            if '{' in key:
                if '_to_' in template_piece:
                    template_subpieces = template_piece.split('_to_')
                    filename_subpieces = filename_piece.split('_to_')
                else:
                    raise Exception('cannot parse')
                assert len(template_subpieces) == len(filename_subpieces)
                for template_subpiece, filename_subpiece in zip(
                    template_subpieces, filename_subpieces
                ):
                    if template_subpiece.startswith('{'):
                        keys[template_subpiece] = filename_subpiece

            else:
                keys[key] = filename_piece

    return keys

