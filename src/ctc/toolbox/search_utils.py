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


def nary_search(
    nary, start_index, end_index, is_match, debug=False, raise_if_not_found=True
):

    extra_probes = [start_index, end_index]
    probe_min = start_index
    probe_max = end_index

    while True:

        if probe_max == probe_min + 1:
            return probe_max

        n_probes = min(nary - 1, probe_max - probe_min - 1)
        d = (probe_max - probe_min) / (n_probes + 1)
        probes = [probe_min + (p + 1) * d for p in range(n_probes)]
        probes = [round(probe) for probe in probes]
        probes = sorted(set(probes))
        n_probes = len(probes)

        all_probes = probes + extra_probes
        all_results = is_match(all_probes)
        results = all_results[:n_probes]
        extra_results = all_results[n_probes:]

        if len(extra_probes) > 0:
            start_result, end_result = extra_results
            if start_result:
                return start_index
            elif not end_result:
                if raise_if_not_found:
                    raise Exception('search range does not go high enough')
                else:
                    return None
            extra_probes = []

        # determine lowest successful probe
        for p in range(len(probes)):
            if results[p]:
                break
        else:
            p += 1

        if debug:
            print('probe_min:', probe_min)
            print('probe_max:', probe_max)
            print('n_probes:', n_probes)
            print('d:', d)
            print('probes:', probes)
            print('results:', results)
            print('p:', p)
            print()

        # adjust search boundaries
        if p == 0:
            probe_min = probe_min
            probe_max = probes[0]
        elif p == len(probes):
            probe_min = probes[-1]
            probe_max = probe_max
        else:
            probe_min = probes[p - 1]
            probe_max = probes[p]

