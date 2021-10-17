import boto3
import toolcache


@toolcache.cache('memory')
def get_s3_client():
    return boto3.client('s3')


@toolcache.cache('memory')
def get_s3_resource():
    return boto3.resource('s3')


