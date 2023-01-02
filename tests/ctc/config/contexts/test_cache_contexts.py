import pytest

import ctc


example_context_config = {
    'db_configs': {
        'local_sqlite': {'dbms': 'sqlite', 'path': ''},
        'local_postgres': {'dbms': 'sqlite', 'path': ''},
    },
    'context_cache_rules': [
        {
            'backend': 'local_sqlite',
            'read': True,
            'write': True,
        },
    ],
}

context_tests = [
    #
    # single boolean global cache
    {
        'context': {'cache': True},
        # default
        'schema_caches': {
            'blocks': ('local_sqlite', True, True),
            'transactions': ('local_sqlite', True, True),
        },
    },
    {
        'context': {'cache': False},
        'schema_caches': {
            'blocks': ('local_sqlite', False, False),
            'transactions': ('local_sqlite', False, False),
        },
    },
    #
    # single boolean read or write cache
    {
        'context': {'cache': {'read': False}},
        'schema_caches': {
            'blocks': ('local_sqlite', False, True),
            'transactions': ('local_sqlite', False, True),
        },
    },
    {
        'context': {'cache': {'read': True}},
        'schema_caches': {
            'blocks': ('local_sqlite', True, True),
            'transactions': ('local_sqlite', True, True),
        },
    },
    {
        'context': {'cache': {'write': False}},
        'schema_caches': {
            'blocks': ('local_sqlite', True, False),
            'transactions': ('local_sqlite', True, False),
        },
    },
    {
        'context': {'cache': {'write': True}},
        'schema_caches': {
            'blocks': ('local_sqlite', True, True),
            'transactions': ('local_sqlite', True, True),
        },
    },
    #
    # double boolean read or write cache
    {
        'context': {'cache': {'read': True, 'write': True}},
        'schema_caches': {
            'blocks': ('local_sqlite', True, True),
            'transactions': ('local_sqlite', True, True),
        },
    },
    {
        'context': {'cache': {'read': False, 'write': False}},
        'schema_caches': {
            'blocks': ('local_sqlite', False, False),
            'transactions': ('local_sqlite', False, False),
        },
    },
    {
        'context': {'cache': {'read': True, 'write': False}},
        'schema_caches': {
            'blocks': ('local_sqlite', True, False),
            'transactions': ('local_sqlite', True, False),
        },
    },
    {
        'context': {'cache': {'read': False, 'write': True}},
        'schema_caches': {
            'blocks': ('local_sqlite', False, True),
            'transactions': ('local_sqlite', False, True),
        },
    },
    #
    # single name of backend
    {
        'context': {'cache': 'local_sqlite'},
        'schema_caches': {
            'blocks': ('local_sqlite', True, True),
            'transactions': ('local_sqlite', True, True),
        },
    },
    {
        'context': {'cache': 'local_postgres'},
        'schema_caches': {
            'blocks': ('local_postgres', True, True),
            'transactions': ('local_postgres', True, True),
        },
    },
    #
    # single name of cache with single boolean read or write
    {
        'context': {'cache': {'backend': 'local_sqlite', 'read': True}},
        'schema_caches': {
            'blocks': ('local_sqlite', True, True),
            'transactions': ('local_sqlite', True, True),
        },
    },
    {
        'context': {'cache': {'backend': 'local_sqlite', 'write': True}},
        'schema_caches': {
            'blocks': ('local_sqlite', True, True),
            'transactions': ('local_sqlite', True, True),
        },
    },
    {
        'context': {'cache': {'backend': 'local_sqlite', 'read': False}},
        'schema_caches': {
            'blocks': ('local_sqlite', False, True),
            'transactions': ('local_sqlite', False, True),
        },
    },
    {
        'context': {'cache': {'backend': 'local_sqlite', 'write': False}},
        'schema_caches': {
            'blocks': ('local_sqlite', True, False),
            'transactions': ('local_sqlite', True, False),
        },
    },
    {
        'context': {'cache': {'backend': 'local_postgres', 'read': True}},
        'schema_caches': {
            'blocks': ('local_postgres', True, True),
            'transactions': ('local_postgres', True, True),
        },
    },
    {
        'context': {'cache': {'backend': 'local_postgres', 'write': True}},
        'schema_caches': {
            'blocks': ('local_postgres', True, True),
            'transactions': ('local_postgres', True, True),
        },
    },
    {
        'context': {'cache': {'backend': 'local_postgres', 'read': False}},
        'schema_caches': {
            'blocks': ('local_postgres', False, True),
            'transactions': ('local_postgres', False, True),
        },
    },
    {
        'context': {'cache': {'backend': 'local_postgres', 'write': False}},
        'schema_caches': {
            'blocks': ('local_postgres', True, False),
            'transactions': ('local_postgres', True, False),
        },
    },
    #
    # single name of cache with double boolean read or write
    {
        'context': {
            'cache': {'backend': 'local_sqlite', 'read': False, 'write': False}
        },
        'schema_caches': {
            'blocks': ('local_sqlite', False, False),
            'transactions': ('local_sqlite', False, False),
        },
    },
    {
        'context': {
            'cache': {'backend': 'local_sqlite', 'read': True, 'write': False}
        },
        'schema_caches': {
            'blocks': ('local_sqlite', True, False),
            'transactions': ('local_sqlite', True, False),
        },
    },
    {
        'context': {
            'cache': {'backend': 'local_sqlite', 'read': False, 'write': True}
        },
        'schema_caches': {
            'blocks': ('local_sqlite', False, True),
            'transactions': ('local_sqlite', False, True),
        },
    },
    {
        'context': {
            'cache': {'backend': 'local_sqlite', 'read': True, 'write': True}
        },
        'schema_caches': {
            'blocks': ('local_sqlite', True, True),
            'transactions': ('local_sqlite', True, True),
        },
    },
    {
        'context': {
            'cache': {
                'backend': 'local_postgres',
                'read': False,
                'write': False,
            }
        },
        'schema_caches': {
            'blocks': ('local_postgres', False, False),
            'transactions': ('local_postgres', False, False),
        },
    },
    {
        'context': {
            'cache': {'backend': 'local_postgres', 'read': True, 'write': False}
        },
        'schema_caches': {
            'blocks': ('local_postgres', True, False),
            'transactions': ('local_postgres', True, False),
        },
    },
    {
        'context': {
            'cache': {'backend': 'local_postgres', 'read': False, 'write': True}
        },
        'schema_caches': {
            'blocks': ('local_postgres', False, True),
            'transactions': ('local_postgres', False, True),
        },
    },
    {
        'context': {
            'cache': {'backend': 'local_postgres', 'read': True, 'write': True}
        },
        'schema_caches': {
            'blocks': ('local_postgres', True, True),
            'transactions': ('local_postgres', True, True),
        },
    },
    #
    # nested cache single boolean
    {
        'context': {'cache': {'blocks': False}},
        'schema_caches': {
            'blocks': ('local_sqlite', False, False),
            'transactions': ('local_sqlite', True, True),
        },
    },
    {
        'context': {'cache': {'blocks': True}},
        'schema_caches': {
            'blocks': ('local_sqlite', True, True),
            'transactions': ('local_sqlite', True, True),
        },
    },
    {
        'context': {'cache': {'transactions': False}},
        'schema_caches': {
            'blocks': ('local_sqlite', True, True),
            'transactions': ('local_sqlite', False, False),
        },
    },
    {
        'context': {'cache': {'transactions': True}},
        'schema_caches': {
            'blocks': ('local_sqlite', True, True),
            'transactions': ('local_sqlite', True, True),
        },
    },
    #
    # nested cache two boolean
    {
        'context': {'cache': {'blocks': False, 'transactions': False}},
        'schema_caches': {
            'blocks': ('local_sqlite', False, False),
            'transactions': ('local_sqlite', False, False),
        },
    },
    {
        'context': {'cache': {'blocks': True, 'transactions': False}},
        'schema_caches': {
            'blocks': ('local_sqlite', True, True),
            'transactions': ('local_sqlite', False, False),
        },
    },
    {
        'context': {'cache': {'blocks': False, 'transactions': True}},
        'schema_caches': {
            'blocks': ('local_sqlite', False, False),
            'transactions': ('local_sqlite', True, True),
        },
    },
    {
        'context': {'cache': {'blocks': True, 'transactions': True}},
        # default
        'schema_caches': {
            'blocks': ('local_sqlite', True, True),
            'transactions': ('local_sqlite', True, True),
        },
    },
    #
    # nested cache boolean mixed with name
    {
        'context': {'cache': {'blocks': 'local_sqlite', 'transactions': False}},
        'schema_caches': {
            'blocks': ('local_sqlite', True, True),
            'transactions': ('local_sqlite', False, False),
        },
    },
    {
        'context': {'cache': {'blocks': 'local_sqlite', 'transactions': True}},
        'schema_caches': {
            'blocks': ('local_sqlite', True, True),
            'transactions': ('local_sqlite', True, True),
        },
    },
    {
        'context': {
            'cache': {'blocks': 'local_postgres', 'transactions': False}
        },
        'schema_caches': {
            'blocks': ('local_postgres', True, True),
            'transactions': ('local_sqlite', False, False),
        },
    },
    {
        'context': {
            'cache': {'blocks': 'local_postgres', 'transactions': True}
        },
        'schema_caches': {
            'blocks': ('local_postgres', True, True),
            'transactions': ('local_sqlite', True, True),
        },
    },
    {
        'context': {'cache': {'blocks': False, 'transactions': 'local_sqlite'}},
        'schema_caches': {
            'blocks': ('local_sqlite', False, False),
            'transactions': ('local_sqlite', True, True),
        },
    },
    {
        'context': {'cache': {'blocks': True, 'transactions': 'local_sqlite'}},
        'schema_caches': {
            'blocks': ('local_sqlite', True, True),
            'transactions': ('local_sqlite', True, True),
        },
    },
    {
        'context': {
            'cache': {'blocks': False, 'transactions': 'local_postgres'}
        },
        'schema_caches': {
            'blocks': ('local_sqlite', False, False),
            'transactions': ('local_postgres', True, True),
        },
    },
    {
        'context': {
            'cache': {'blocks': True, 'transactions': 'local_postgres'}
        },
        'schema_caches': {
            'blocks': ('local_sqlite', True, True),
            'transactions': ('local_postgres', True, True),
        },
    },
    #
    # nested cache two names
    {
        'context': {
            'cache': {
                'blocks': 'local_sqlite',
                'transactions': 'local_sqlite',
            },
        },
        'schema_caches': {
            'blocks': ('local_sqlite', True, True),
            'transactions': ('local_sqlite', True, True),
        },
    },
    {
        'context': {
            'cache': {
                'blocks': 'local_postgres',
                'transactions': 'local_sqlite',
            },
        },
        'schema_caches': {
            'blocks': ('local_postgres', True, True),
            'transactions': ('local_sqlite', True, True),
        },
    },
    {
        'context': {
            'cache': {
                'blocks': 'local_sqlite',
                'transactions': 'local_postgres',
            },
        },
        'schema_caches': {
            'blocks': ('local_sqlite', True, True),
            'transactions': ('local_postgres', True, True),
        },
    },
    {
        'context': {
            'cache': {
                'blocks': 'local_postgres',
                'transactions': 'local_postgres',
            },
        },
        'schema_caches': {
            'blocks': ('local_postgres', True, True),
            'transactions': ('local_postgres', True, True),
        },
    },
    #
    # [double nested versions of everything above]
    # ...
]


# add double nested tests
default_cache_config = example_context_config['context_cache_rules'][-1]
default_tuple = (
    default_cache_config['backend'],
    default_cache_config['read'],
    default_cache_config['write'],
)
subconfigs = [
    {'backend': 'local_sqlite'},
    {'backend': 'local_postgres'},
    {'read': True},
    {'read': False},
    {'write': True},
    {'write': False},
    {'read': True, 'write': True},
    {'read': True, 'write': False},
    {'read': False, 'write': True},
    {'read': False, 'write': False},
    {'backend': 'local_sqlite', 'read': True},
    {'backend': 'local_sqlite', 'read': False},
    {'backend': 'local_sqlite', 'write': True},
    {'backend': 'local_sqlite', 'write': False},
    {'backend': 'local_sqlite', 'read': True, 'write': True},
    {'backend': 'local_sqlite', 'read': True, 'write': False},
    {'backend': 'local_sqlite', 'read': False, 'write': True},
    {'backend': 'local_sqlite', 'read': False, 'write': False},
    {'backend': 'local_postgres', 'read': True},
    {'backend': 'local_postgres', 'read': False},
    {'backend': 'local_postgres', 'write': True},
    {'backend': 'local_postgres', 'write': False},
    {'backend': 'local_postgres', 'read': True, 'write': True},
    {'backend': 'local_postgres', 'read': True, 'write': False},
    {'backend': 'local_postgres', 'read': False, 'write': True},
    {'backend': 'local_postgres', 'read': False, 'write': False},
]
for subconfig in subconfigs:

    full_subconfig = dict(default_cache_config, **subconfig)
    subconfig_tuple = (
        full_subconfig['backend'],
        full_subconfig['read'],
        full_subconfig['write'],
    )

    test_1 = {
        'context': {'cache': {'blocks': subconfig}},
        'schema_caches': {
            'blocks': subconfig_tuple,
            'transactions': default_tuple,
        },
    }
    test_2 = {
        'context': {'cache': {'transactions': subconfig}},
        'schema_caches': {
            'blocks': default_tuple,
            'transactions': subconfig_tuple,
        },
    }
    test_3 = {
        'context': {'cache': {'blocks': subconfig, 'transactions': subconfig}},
        'schema_caches': {
            'blocks': subconfig_tuple,
            'transactions': subconfig_tuple,
        },
    }
    test_4 = {
        'context': {'cache': {'blocks': subconfig, 'transactions': False}},
        'schema_caches': {
            'blocks': subconfig_tuple,
            'transactions': ('local_sqlite', False, False),
        },
    }
    test_5 = {
        'context': {'cache': {'blocks': False, 'transactions': subconfig}},
        'schema_caches': {
            'blocks': ('local_sqlite', False, False),
            'transactions': subconfig_tuple,
        },
    }

    context_tests.append(test_1)
    context_tests.append(test_2)
    context_tests.append(test_3)
    context_tests.append(test_4)
    context_tests.append(test_5)


@pytest.fixture()
def set_example_context_config():
    import ctc.config

    for key, value in example_context_config.items():
        ctc.config.set_config_override(key=key, value=value)

    yield

    ctc.config.clear_all_config_overrides()


@pytest.mark.parametrize('test', context_tests)
def test_get_context_schema_cache(test, set_example_context_config):
    context = test['context']

    schema_caches = test.get('schema_caches')
    if schema_caches is not None:
        for schema_name, target_schema_cache in schema_caches.items():
            actual_backend = ctc.config.get_context_cache_backend(
                schema_name=schema_name, context=context
            )
            read_cache, write_cache = ctc.config.get_context_cache_read_write(
                schema_name=schema_name, context=context
            )
            assert (
                actual_backend,
                read_cache,
                write_cache,
            ) == target_schema_cache


#
# # test interaction with config variables
#

# def test_global_cache_override():
#     pass


# def test_global_cache_override():
#     pass


# def test_global_cache_override():
#     pass


# def test_global_cache_override():
#     pass

