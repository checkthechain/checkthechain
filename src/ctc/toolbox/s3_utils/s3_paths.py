import os

from fei import config_utils


def get_s3_uri(s3_uri=None, bucket=None, key=None, local_path=None):

    if s3_uri is not None:
        return s3_uri
    else:
        bucket, key = get_s3_bucket_and_key(
            bucket=bucket, key=key, local_path=local_path
        )
        return os.path.join('s3://' + bucket, key)


def get_s3_bucket_and_key(s3_uri=None, bucket=None, key=None, local_path=None):

    if bucket is None:
        bucket = config_utils.get_config()['s3_bucket']

    if key is None:

        if s3_uri is not None:

            # if s3_uri given, split into bucket and key
            head, tail = s3_uri.split('s3://')
            bucket, key = tail.split('/', maxsplit=1)

        elif local_path is not None:

            # if file str given, use default bucket and key relative to data_root
            bucket, key = _local_path_to_bucket_and_key(local_path)

        elif bucket is not None:

            if key is None:
                key = ''

        else:

            raise Exception('must specify s3_uri, local_path, or bucket and key')

    return bucket, key


def _local_path_to_bucket_and_key(local_path):
    config = config_utils.get_config()
    bucket = config['s3_bucket']
    data_root = config['data_root']
    if local_path.startswith('/'):
        if local_path.startswith(data_root):
            key = os.path.relpath(local_path, data_root)
        else:
            raise Exception('could not determine key outside data_root')
    else:
        key = local_path
    return bucket, key


def contextualize_local_path(local_path):
    """relative paths are prepended with data_root"""
    if not local_path.startswith('/'):
        config = config_utils.get_config()
        local_path = os.path.join(config['data_root'], local_path)
    return local_path

