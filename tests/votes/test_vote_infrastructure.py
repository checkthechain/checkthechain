import os

import fei.data


def test_request_raw_vote_data():
    fei.data.request_raw_vote_data(fip=1)


def test_get_vote_data_dir():
    data_dir = fei.data.get_vote_data_dir()
    assert os.path.isdir(data_dir)

