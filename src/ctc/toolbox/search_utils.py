
class NotFoundException(Exception):
    pass


def binary_search(
    *,
    is_match,
    start_index=None,
    end_index=None,
    index_range=None,
    raise_if_not_found=True
):
    """return the first index for which match returns True"""

    if start_index is None and end_index is None:
        start_index, end_index = index_range

    start_index = int(start_index)
    end_index = int(end_index)

    if is_match(start_index):
        return start_index
    if not is_match(end_index):
        if raise_if_not_found:
            raise NotFoundException('could not find match')
        else:
            return None

    while True:

        midpoint = (start_index + end_index) / 2
        midpoint = int(midpoint)

        if is_match(midpoint):
            end_index = midpoint
        else:
            start_index = midpoint

        if start_index + 1 == end_index:
            return end_index


def parallel_binary_search(is_match, start_index, end_index, n_workers=10):
    # not super effective, since it has to evaluate the borders
    # also need to move is_match to be a top level function
    # more effective would be a parallel_nary_search, each round does n samples
    # should just use cloudpickle as well
    chunk_bounds = range(
        int(start_index),
        int(end_index),
        int((end_index - start_index) / (n_workers + 1)),
    )
    chunk_bounds = list(chunk_bounds)
    chunks = zip(chunk_bounds[:-1], [item - 1 for item in chunk_bounds[1:]])
    chunks = list(chunks)
    chunk_results = binary_search(
        index_ranges=chunks,
        is_match=is_match,
        raise_if_not_found=False,
    )
    for chunk_result in chunk_results:
        if chunk_result is not None:
            return chunk_result
    else:
        return chunk_result


def parallel_nary_search():
    pass

