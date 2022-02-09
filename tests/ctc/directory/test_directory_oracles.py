import pytest
import toolconfig

from ctc import spec
from ctc import directory


@pytest.mark.parametrize(
    'test',
    [
        ['chainlink', 'ETH_USD', '0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419'],
    ],
)
def test_get_oracle_address(test):
    protocol, feed_name, feed_address = test
    actual_address = directory.get_oracle_address(
        name=feed_name,
        protocol=protocol,
    )
    assert actual_address == feed_address


def test_get_oracle_feed_metadata():
    metadata = directory.get_oracle_feed_metadata(name='ETH_USD')
    toolconfig.conforms_to_spec(metadata, spec.OracleFeedMetadata)


def test_load_oracle_feeds():
    oracle_feeds = directory.load_oracle_feeds()
    for metadata in oracle_feeds.values():
        toolconfig.conforms_to_spec(metadata, spec.OracleFeedMetadata)


def test_get_oracle_feed_path():
    path = directory.get_oracle_feed_path()
    assert isinstance(path, str) and len(path) > 0

