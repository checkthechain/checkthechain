"""compare different implementations of state snapshots"""

import copy
import time

import numba

import fei
from fei.toolbox import copy_utils


n_steps = int(1e5)

initial_state_nested = fei.initialize_state()
initial_state_flat = fei.initialize_state_flat()
initial_state_array = fei.initialize_state_array(size=n_steps)


#
# # utility functions
#

@numba.jit(nopython=True)
def update_array_snapshots(array):
    for i in range(1, n_steps):
        array[i, :] = array[i - 1, :]


#
# # snapshot functions
#

def snapshot_nested_shallow():
    snapshots = []
    for i in range(n_steps):
        snapshot = copy.copy(initial_state_nested)
        snapshots.append(snapshot)
    return snapshots


def snapshot_nested_deep():
    snapshots = []
    for i in range(n_steps):
        snapshot = copy.deepcopy(initial_state_nested)
        snapshots.append(snapshot)
    return snapshots


def snapshot_nested_hierarchy():
    snapshots = []
    for i in range(n_steps):
        snapshot = copy_utils.copy_hierarchy(initial_state_nested)
        snapshots.append(snapshot)
    return snapshots


def snapshot_flat_shallow():
    snapshots = []
    for i in range(n_steps):
        snapshot = dict(initial_state_nested)
        snapshots.append(snapshot)
    return snapshots


def snapshot_flat_hierarchy():
    snapshots = []
    for i in range(n_steps):
        snapshot = copy_utils.copy_hierarchy(initial_state_nested)
        snapshots.append(snapshot)
    return snapshots


def snapshot_array_loop():
    array = initial_state_array['state']
    for i in range(1, n_steps):
        array[i, :] = array[i - 1, :]
    return array


def snapshot_array_jit():
    array = initial_state_array['state']
    update_array_snapshots(array)


#
# # test runner
#

def run_test():

    versions = [
        snapshot_nested_shallow,
        # snapshot_nested_deep,  # too slow to even test
        snapshot_nested_hierarchy,
        snapshot_flat_shallow,
        snapshot_flat_hierarchy,
        snapshot_array_jit,
        snapshot_array_loop,
    ]

    # warmup
    for version in versions:
        version()

    # test
    print('testing snapshot implementations')
    print()

    for version in versions:
        start = time.time()
        version()
        end = time.time()
        print(version.__name__ + ':', end - start)

    print()
    print('done')


#
# # script
#

if __name__ == '__main__':
    run_test()

