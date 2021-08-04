#!/usr/bin/env python3

from fei.data import etl
from fei.data import directory

token_addresses = [
    directory.token_addresses['FEI'],
    directory.token_addresses['TRIBE'],
    directory.token_addresses['FGEN'],
    directory.token_addresses['univ2_FEI_ETH'],
    directory.token_addresses['univ2_FEI_TRIBE'],
]

# extract etl data relevant to fei
etl.extract_token_subsets(
    source_view='raw',
    target_view='fei_ecosystem',
    token_addresses=token_addresses,
)

# extract logs relevant to fei
etl.export_receipts_and_logs_of_transactions(etl_view='fei_ecosystem')

