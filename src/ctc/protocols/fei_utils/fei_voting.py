# type: ignore
"""this is very old code, needs to be refactored"""
from __future__ import annotations

import copy
import json
import os
import typing
from typing_extensions import TypedDict

import tooltime

from ctc import spec


vote_data_file_template = '{name}__{datatype}__{timestamp}.json'

datatypes = [
    'choices',
    'scores',
]

proposal_hashes = {
    'FIP_1': 'QmWYNqr9Rcn8QFiZYyRqjQno3jXTToy3vM4bVKJkuntvoz',
}

url_templates = {
    'choices': 'https://hub.snapshot.org/api/fei.eth/proposal/{proposal_hash}',
}

choice_names = {
    'FIP_1': {1: 'no change', 2: '$1.00 / FEI', 3: '$0.90 / FEI'},
}


#
# # internet requests
#


def request_raw_vote_data(
    name: str,
    *,
    save: bool = True,
    overwrite: bool = False,
    verbose: bool = True,
) -> dict:

    # create url
    url = url_templates['choices'].format(proposal_hash=proposal_hashes[name])

    if verbose:
        print('requesting proposal', name)

    # request data
    import requests

    response = requests.get(url=url)
    data = response.json()

    # save data
    if save:
        timestamp = tooltime.create_timestamp_label()
        path = get_vote_data_path(
            name=name, datatype='choices', timestamp=timestamp
        )
        if os.path.isfile(path) and not overwrite:
            raise Exception('path already exists: ' + str(path))
        with open(path, 'w') as f:
            json.dump(data, f)

        if verbose:
            print('saving to:', path)

    return data


#
# # data paths
#


def get_vote_data_dir() -> str:
    raise NotImplementedError()


def get_vote_data_path(*, name: str, datatype: str, timestamp: str) -> str:
    filename = vote_data_file_template.format(
        name=name,
        datatype=datatype,
        timestamp=timestamp,
    )
    return os.path.join(get_vote_data_dir(), filename)


def get_vote_data_files(
    name: str | None = None,
    datatype: str | None = None,
) -> list[dict[str, str]]:

    vote_data_dir = get_vote_data_dir()

    files = []
    for filename in sorted(os.listdir(vote_data_dir)):

        if not os.path.isfile(os.path.join(vote_data_dir, filename)):
            continue

        parsed = parse_filename(filename)

        if name is not None and parsed['name'] != name:
            continue
        if datatype is not None and parsed['datatype'] != datatype:
            continue

        data = dict(parsed)
        data['path'] = os.path.join(vote_data_dir, filename)

        files.append(data)

    if datatype is not None:
        files = [file for file in files if file['datatype'] == datatype]

    return files


def parse_filename(filename: str) -> dict[str, str]:
    name, datatype, timestamp = os.path.splitext(filename)[0].split('__')
    return {
        'name': name,
        'datatype': datatype,
        'timestamp': timestamp,
    }


#
# # io
#


def load_raw_vote_data(
    name: str,
    datatype: str,
    *,
    request: bool | None = None,
    timestamp: str | None = None,
    verbose: bool = True,
) -> dict:
    """load vote data from disk, requesting it online if necessary"""

    path = None

    if request is not None and timestamp is not None:
        raise Exception('cannot specify both request and timestamp')

    elif timestamp is not None:
        # load specified file
        path = get_vote_data_path(
            name=name,
            datatype=datatype,
            timestamp=timestamp,
        )

    elif request is None and timestamp is None:
        # load most recent matching file
        files = get_vote_data_files(name=name, datatype=datatype)
        if len(files) > 0:
            path = files[-1]['path']

    # load data
    if path is not None:
        # load file
        if verbose:
            print('loading data path', path)
        with open(path, 'r') as f:
            return json.load(f)
    else:
        # request data
        return request_raw_vote_data(name=name, verbose=verbose)


#
# # crud
#


class Vote(TypedDict):
    address: spec.Address
    timestamp: str
    choice: str
    scores: typing.Sequence[int]
    scores_total: spec.Number


def get_vote_data(
    name: str,
    load_kwargs: dict | None = None,
) -> typing.Mapping[spec.Address, Vote]:

    # get raw data
    if load_kwargs is None:
        load_kwargs = {}
    load_kwargs = dict(load_kwargs)
    load_kwargs['name'] = name
    choices = load_raw_vote_data(datatype='choices', **load_kwargs)
    scores = load_raw_vote_data(datatype='scores', **load_kwargs)
    strategies = scores.keys()

    # process raw data
    votes = {}
    for address, raw in choices.items():
        address_scores = {
            strategy: float(scores[strategy][address])
            for strategy in strategies
        }

        # eliminate corrupted votes
        choice = raw['msg']['payload']['choice']
        if isinstance(choice, dict):
            continue

        address = address.lower()
        votes[address] = {
            'address': address,
            'timestamp': raw['msg']['timestamp'],
            'choice': choice,
            'scores': address_scores,
            'scores_total': sum(address_scores.values()),
        }

    return votes


def create_vote_dataframe(
    votes: typing.Mapping[spec.Address, Vote],
    *,
    tags_of_addresses: typing.Mapping[str, typing.Mapping[str, str]]
    | None = None,
    addresses_of_tags: typing.Mapping[str, typing.Mapping[str, str]]
    | None = None,
) -> spec.DataFrame:
    """

    ## Inputs
    - votes: vote data returned by get_vote_data()
    - addresses_of_tags: {tag_name: {address: tag_value}}
    - tags_of_addresses: {address: {tag_name: tag_value}}
    """

    import pandas as pd

    votes = copy.deepcopy(votes)

    # create separate column for each voting strategy
    strategy_scores = {}
    for address, vote in votes.items():
        for strategy, strategy_score in vote['scores'].items():
            strategy_scores.setdefault(strategy, {})
            strategy_scores[strategy][address] = strategy_score
    if addresses_of_tags is None:
        addresses_of_tags = {}
    for strategy in strategy_scores:
        addresses_of_tags.setdefault(
            'score_' + strategy, strategy_scores[strategy]
        )

    # set tag values
    if tags_of_addresses is not None:
        for address in tags_of_addresses.keys():
            if address in votes:
                for tag_name, tag_value in tags_of_addresses.items():
                    votes[address][tag_name] = tag_value
    if addresses_of_tags is not None:
        for tag_name in addresses_of_tags.keys():
            for address, tag_value in addresses_of_tags[tag_name].items():
                if address in votes:
                    votes[address][tag_name] = tag_value

    votes_df = pd.DataFrame(votes).transpose()

    # convert dtypes
    votes_df = votes_df.convert_dtypes()
    votes_df = votes_df.replace(np.nan, 0)

    return votes_df
