import os
import tempfile

import pytest
import toolsql

from ctc import db
from ctc.protocols.chainlink_utils import chainlink_db
from ctc.protocols import fourbyte_utils
from ctc.protocols.coingecko_utils import coingecko_db


schema_datas = [
    {
        'schema_name': 'block_timestamps',
        'selector': db.schemas.block_timestamps.async_select_block_timestamp,
        'queryer': db.schemas.block_timestamps.async_query_block_timestamp,
        'query': {'block_number': 100},
        'plural_selector': db.schemas.block_timestamps.async_select_block_timestamps,
        'plural_queryer': db.schemas.block_timestamps.async_query_block_timestamp,
        'plural_query': {'block_numbers': [100, 200, 300]},
    },
    {
        'schema_name': 'block_timestamps',
        'selector': db.schemas.block_timestamps.async_select_max_block_timestamp,
        'queryer': db.schemas.block_timestamps.async_query_max_block_timestamp,
        'query': {},
    },
    {
        'schema_name': 'block_timestamps',
        'selector': db.schemas.blocks.blocks_statements.async_select_max_block_number,
        # 'queryer': db.schemas.blocks.blocks_statements.async_query_max_block_number,
        'query': {},
    },
    {
        'schema_name': 'block_timestamps',
        'selector': db.schemas.blocks.blocks_statements.async_select_max_block_timestamp,
        # 'queryer': db.schemas.blocks.blocks_statements.async_query_max_block_timestamp,
        'query': {},
    },
    {
        'schema_name': 'blocks',
        'selector': db.schemas.blocks.async_select_block,
        'queryer': db.schemas.blocks.async_query_block,
        'query': {'block_number': 100},
        'plural_selector': db.schemas.blocks.async_select_blocks,
        'plural_queryer': db.schemas.blocks.async_query_blocks,
        'plural_query': {'block_numbers': [100, 200, 300]},
    },
    {
        'schema_name': 'contract_abis',
        'selector': db.async_select_contract_abi,
        'queryer': db.async_query_contract_abi,
        'query': {'address': '0x956f47f50a910163d8bf957cf5846d573e7f87ca'},
        'plural_selector': db.async_select_contract_abis,
        'plural_queryer': db.async_query_contract_abis,
        'plural_query': {},
    },
    {
        'schema_name': 'contract_creation_blocks',
        'selector': db.async_select_contract_creation_block,
        'queryer': db.async_query_contract_creation_block,
        'query': {'address': '0x956f47f50a910163d8bf957cf5846d573e7f87ca'},
        'plural_selector': db.async_select_contract_creation_blocks,
        'plural_queryer': db.async_query_contract_creation_blocks,
        'plural_query': {},
    },
    {
        'schema_name': 'erc20_metadata',
        'selector': db.async_select_erc20_metadata,
        'queryer': db.async_query_erc20_metadata,
        'query': {'address': '0x956f47f50a910163d8bf957cf5846d573e7f87ca'},
        'plural_selector': db.async_select_erc20s_metadata,
        'plural_queryer': db.async_query_erc20s_metadata,
        'plural_query': {
            'addresses': ['0x956f47f50a910163d8bf957cf5846d573e7f87ca'],
        },
    },
    {
        'schema_name': 'dex_pools',
        'selector': db.async_select_dex_pool,
        'queryer': db.async_query_dex_pool,
        'query': {'address': '0x9928e4046d7c6513326ccea028cd3e7a91c7590a'},
        'plural_selector': db.async_select_dex_pools,
        'plural_queryer': db.async_query_dex_pools,
        'plural_query': {
            'factory': '0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f',
        },
    },
    {
        'schema_name': 'chainlink',
        'selector': chainlink_db.async_select_feed,
        'queryer': chainlink_db.async_query_feed,
        'query': {'address': '0x31e0a88fecb6ec0a411dbe0e9e76391498296ee9'},
        'plural_selector': chainlink_db.async_select_feeds,
        'plural_queryer': chainlink_db.async_query_feeds,
        'plural_query': {
            'addresses': ['0x31e0a88fecb6ec0a411dbe0e9e76391498296ee9'],
        },
    },
    {
        'schema_name': '4byte',
        # 'selector': fourbyte_utils.async_select_function_entries,
        # 'queryer': fourbyte_utils.async_query_function_entries,
        # 'query': {'address': '0x31e0a88fecb6ec0a411dbe0e9e76391498296ee9'},
        'plural_selector': fourbyte_utils.async_select_function_signatures,
        'plural_queryer': fourbyte_utils.async_query_function_signatures,
        'plural_query': {
            'text_signature': 'transfer(address,uint256)',
        },
    },
    {
        'schema_name': 'coingecko',
        'selector': coingecko_db.async_select_token,
        'queryer': coingecko_db.async_query_token,
        'query': {'id': '1244-s-avers'},
        'plural_selector': coingecko_db.async_select_tokens,
        'plural_queryer': coingecko_db.async_query_tokens,
        'plural_query': {
            'symbol_query': 'eth',
        },
    },
    {
        'schema_name': 'block_gas',
        'selector': db.async_select_median_block_gas_fee,
        'queryer': db.async_query_median_block_gas_fee,
        'query': {'block_number': 14000000},
        'plural_selector': db.async_select_median_blocks_gas_fees,
        'plural_queryer': db.async_query_median_blocks_gas_fees,
        'plural_query': {'block_numbers': [14000000, 14000001, 14000002]},
    },
]

non_network_schemas = (
    db.get_generic_schema_names() + db.get_admin_schema_names()
)


def get_test_db_config():
    tempdir = tempfile.mkdtemp()
    return {
        'dbms': 'sqlite',
        'path': os.path.join(tempdir, 'example.db'),
    }


def test_all_evm_schemas_tested_for_problems():
    tested = {schema_datum['schema_name'] for schema_datum in schema_datas}
    assert tested == set(
        db.get_network_schema_names() + db.get_generic_schema_names()
    ), 'not all EVM schema types being tested for common db problems'


@pytest.mark.parametrize('schema_data', schema_datas)
async def test_select_when_db_folder_does_not_exist(schema_data):

    dne_dir = os.path.join(tempfile.mkdtemp(), 'does', 'not', 'exist')
    assert not os.path.isdir(dne_dir)

    db_config = {
        'dbms': 'sqlite',
        'path': dne_dir,
    }
    engine = toolsql.create_engine(**db_config)

    if schema_data.get('queryer') is not None:
        result = await schema_data['queryer'](network=1, engine=engine)

        assert result is None


@pytest.mark.parametrize('schema_data', schema_datas)
async def test_select_when_db_file_does_not_exist(schema_data):

    db_config = get_test_db_config()
    engine = toolsql.create_engine(**db_config)

    if schema_data.get('queryer') is not None:
        result = await schema_data['queryer'](
            network=1, engine=engine, **schema_data['query']
        )

        assert result is None


@pytest.mark.parametrize('schema_data', schema_datas)
async def test_select_when_schema_not_initialized(schema_data):

    db_config = get_test_db_config()
    engine = toolsql.create_engine(**db_config)
    with engine.begin() as conn:
        db.initialize_schema_versions(conn=conn)

    if schema_data['schema_name'] not in non_network_schemas:
        network_kwargs = {'network': 1}
    else:
        network_kwargs = {}

    if schema_data.get('selector') is not None:
        with engine.begin() as conn:
            result = await schema_data['selector'](
                conn=conn, **schema_data['query'], **network_kwargs
            )

        assert result is None

    if 'plural_selector' in schema_data:
        with engine.begin() as conn:
            result = await schema_data['plural_selector'](
                conn=conn,
                **schema_data['plural_query'],
                **network_kwargs,
            )

        assert result is None


@pytest.mark.parametrize('schema_data', schema_datas)
async def test_query_when_schema_not_initialized(schema_data):

    db_config = get_test_db_config()
    engine = toolsql.create_engine(**db_config)
    with engine.begin() as conn:
        db.initialize_schema_versions(conn=conn)

    if schema_data['schema_name'] not in non_network_schemas:
        network_kwargs = {'network': 1}
    else:
        network_kwargs = {}

    if schema_data.get('queryer') is not None:
        result = await schema_data['queryer'](
            engine=engine, **schema_data['query'], **network_kwargs
        )

        assert result is None


@pytest.mark.parametrize('schema_data', schema_datas)
async def test_select_when_row_does_not_exist(schema_data):

    db_config = get_test_db_config()
    engine = toolsql.create_engine(**db_config)
    with engine.begin() as conn:
        if schema_data['schema_name'] not in non_network_schemas:
            network_kwargs = {'network': 1}
        else:
            network_kwargs = {'network': None}

        db.initialize_schema(
            schema_name=schema_data['schema_name'], conn=conn, **network_kwargs
        )

    if schema_data['schema_name'] not in non_network_schemas:
        network_kwargs = {'network': 1}
    else:
        network_kwargs = {}

    if schema_data.get('selector') is not None:
        with engine.begin() as conn:
            result = await schema_data['selector'](
                conn=conn, **schema_data['query'], **network_kwargs
            )

        assert result is None

    if 'plural_selector' in schema_data:
        with engine.begin() as conn:
            result = await schema_data['plural_selector'](
                conn=conn,
                **schema_data['plural_query'],
                **network_kwargs,
            )

        assert result is None or all(item is None for item in result)


@pytest.mark.parametrize('schema_data', schema_datas)
async def test_query_when_row_does_not_exist(schema_data):

    db_config = get_test_db_config()
    engine = toolsql.create_engine(**db_config)
    with engine.begin() as conn:
        if schema_data['schema_name'] not in non_network_schemas:
            network_kwargs = {'network': 1}
        else:
            network_kwargs = {'network': None}

        db.initialize_schema(
            schema_name=schema_data['schema_name'], conn=conn, **network_kwargs
        )

    if schema_data.get('queryer') is not None:
        if schema_data['schema_name'] not in non_network_schemas:
            network_kwargs = {'network': 1}
        else:
            network_kwargs = {}

        result = await schema_data['queryer'](
            engine=engine, **schema_data['query'], **network_kwargs
        )

        assert result is None
