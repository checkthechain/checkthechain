"""
- revalidation after a reorg is expensive
- should use a large enough confirmation time to make reorgs rare

References on common confirmation thresholds
- https://support.nexo.io/s/article/processing-time-of-cryptocurrency-deposits-blockchain-confirmations
- https://developers.circle.com/developer/docs/confirmations
- https://support.kraken.com/hc/en-us/articles/203325283-Cryptocurrency-deposit-processing-times
"""

from __future__ import annotations

from ctc import spec


def get_required_confirmations(context: spec.Context) -> int:
    # for now use single confirmation age for all datatypes and networks
    return 128
