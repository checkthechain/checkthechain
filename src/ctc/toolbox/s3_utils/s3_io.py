"""mostly wrappers around boto3

- see https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html

for now, no delete functionality included
- perform deletes manually using `aws s3 rm <s3_uri>`
"""
import io

import pandas as pd

from fei import config_utils
from . import s3_paths
from . import s3_objects

#
# # listing
#


def list_objects(
    query=None, *, s3_uri=None, bucket=None, prefix=None, format='paths'
):

    # determine bucket and prefix
    if query is not None:
        if query.startswith('s3://'):
            s3_uri = query
        else:
            prefix = query
    if s3_uri is not None:
        bucket, prefix = s3_paths.get_s3_bucket_and_key(s3_uri=s3_uri)
    if bucket is None:
        bucket = config_utils.get_config()['s3_bucket']
    if prefix is None:
        prefix = ''

    # query data
    s3_client = s3_objects.get_s3_client()
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if 'Contents' in response:
        items = response['Contents']
    else:
        items = []

    # ensure no pagination required
    if len(items) == 1000:
        raise NotImplementedError('need to paginate for more than 1000 entries')

    # format output
    if format == 'paths':
        return [item['Key'] for item in items]
    elif format == 'dataframe':
        return pd.DataFrame(items)
    elif format == 'raw':
        return items
    else:
        raise Exception('unknown format: ' + str(format))

    return items


#
# # uploads
#


def upload_to_s3(
    *,
    local_path=None,
    file_object=None,
    dataframe=None,
    s3_uri=None,
    bucket=None,
    key=None,
    verbose=2,
):

    # get bucket and key
    bucket, key = s3_paths.get_s3_bucket_and_key(
        s3_uri=s3_uri,
        bucket=bucket,
        key=key,
        local_path=local_path,
    )

    if verbose:
        print('uploading to', s3_paths.get_s3_uri(bucket=bucket, key=key))

    if file_object is not None:

        s3_resource = s3_objects.get_s3_resource()
        s3_resource.upload_fileobj(file_object, bucket, key)

    elif dataframe is not None:

        s3_uri = s3_paths.get_s3_uri(
            bucket=bucket,
            key=key,
            s3_uri=s3_uri,
        )
        dataframe.to_csv(s3_uri)

    elif local_path is not None:

        local_path = s3_paths.contextualize_local_path(local_path)
        s3_resource = s3_objects.get_s3_resource()
        s3_resource.meta.client.upload_file(local_path, bucket, key)

    else:
        raise Exception('must specify local_path, file_object, or dataframe')

    if verbose > 1:
        print('upload complete')


#
# # downloads
#


def download_from_s3(
    local_path=None,
    file_object=None,
    s3_uri=None,
    bucket=None,
    key=None,
    verbose=2,
):
    """download data from s3 into file or existing python file object"""

    # get bucket and key
    bucket, key = s3_paths.get_s3_bucket_and_key(
        s3_uri=s3_uri,
        bucket=bucket,
        key=key,
        local_path=local_path,
    )

    if verbose:
        print('downloading to', s3_paths.get_s3_uri(bucket=bucket, key=key))

    s3_resource = s3_objects.get_s3_resource()

    if local_path is not None:

        local_path = s3_paths.contextualize_local_path(local_path)
        s3_resource.meta.client.download_file(local_path, bucket, key)

    elif file_object is not None:

        s3_resource.download_fileobj(
            bucket=bucket, key=key, fileobj=file_object
        )

    else:
        raise Exception('must specify local_path, file_object')

    if verbose > 1:
        print('download complete')


def fetch_from_s3(key, bucket=None, format=None, verbose=2):
    """fetch data from s3 into new python object"""

    if format is None:
        if key.endswith('.csv'):
            format = 'dataframe'
        else:
            raise Exception('unkown format for key: ' + str(key))
    if bucket is None:
        bucket = config_utils.get_config()['s3_bucket']

    if verbose:
        print('fetching', s3_paths.get_s3_uri(bucket=bucket, key=key))

    if format == 'dataframe':
        s3_client = s3_objects.get_s3_client()
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        df = pd.read_csv(io.BytesIO(obj['Body'].read()), encoding='utf8')
        result = df

    elif format == 'file_object':

        s3_client = s3_objects.get_s3_client()
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        result = obj['Body']

    else:
        raise Exception('unknown format: ' + str(format))

    if verbose > 1:
        print('fetch complete')

    return result

