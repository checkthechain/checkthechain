"""
- revalidation after a reorg is expensive
- should use a large enough confirmation time to make reorgs rare
"""

from __future__ import annotations

from ctc import spec


def get_required_confirmations(network: spec.NetworkReference) -> int:
    # for now use single confirmation age for all datatypes and networks
    return 128
