import math


def chunk_blocks_by_size(blocks, n_per_chunk):
    n_chunks = math.ceil(len(blocks) / n_per_chunk)
    return [
        blocks[c * n_per_chunk: (c + 1) * n_per_chunk]
        for c in range(n_chunks)
    ]


def chunk_blocks_into_ranges(blocks, chunk_size):
    chunks_by_group = {}
    for block in blocks:
        group = math.floor(block / chunk_size) * chunk_size
        chunks_by_group.setdefault(group, [])
        chunks_by_group[group].append(block)
    return chunks_by_group


def get_chunks_in_range(start_block, end_block, chunk_size, trim_excess=False):
    """break a range of blocks into chunks of a given chunk size"""
    chunk_start_block = (start_block // chunk_size) * chunk_size
    chunk_end_block = ((end_block // chunk_size) + 1) * chunk_size
    chunk_bounds = list(
        range(chunk_start_block, chunk_end_block + chunk_size, chunk_size)
    )
    chunks = [
        [start, end - 1]
        for start, end in zip(chunk_bounds[:-1], chunk_bounds[1:])
    ]

    if trim_excess:
        if len(chunks) > 0:
            if chunks[0][0] < start_block:
                chunks[0] = [start_block, chunks[0][1]]
            if chunks[-1][-1] > end_block:
                chunks[-1] = [chunks[-1][0], end_block]

    return chunks

