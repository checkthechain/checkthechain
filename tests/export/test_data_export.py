import tempfile

from larp.toolbox import decimal_utils

import fei


n_blocks = 1000

parameters = {
    'run_duration': n_blocks,
    'record_events': True,
}

simulation = fei.FeiSimulation(**parameters)
simulation.run()


def test_snapshots_to_csv():

    # write file
    handle, tmp_path = tempfile.mkstemp()
    simulation.snapshots_to_csv(path=tmp_path, overwrite=True)

    # assert snapshots match
    with open(tmp_path, 'r') as f:
        lines = f.readlines()
    assert len(lines) == len(simulation.snapshots) + 1


def test_events_to_json():

    # write file
    handle, tmp_path = tempfile.mkstemp()
    simulation.events_to_json(path=tmp_path, overwrite=True)

    # assert event records match
    with open(tmp_path, 'r') as f:
        event_data = decimal_utils.json_load(f)

    pairs = [
        [event_data['event_records'], simulation.event_records],
        [event_data['event_pre_metadatas'], simulation.event_pre_metadatas],
        [event_data['event_post_metadatas'], simulation.event_post_metadatas],
        [
            event_data['event_pre_metadata_fields'],
            simulation.event_pre_metadata_fields,
        ],
        [
            event_data['event_post_metadata_fields'],
            simulation.event_post_metadata_fields,
        ],
    ]
    for lhs, rhs in pairs:
        lhs_serialized = decimal_utils.json_dumps(lhs, sort_keys=True)
        rhs_serialized = decimal_utils.json_dumps(rhs, sort_keys=True)
        assert lhs_serialized == rhs_serialized

