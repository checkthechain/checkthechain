import setuptools


setuptools.setup(
    name='checkthechain',
    version='0.2.10',
    packages=setuptools.find_packages("./src"),
    package_dir={'': 'src'},
    package_data={
        'ctc': [
            'default_data/*',
            'default_data/*/*',
            'default_data/*/*/*',
        ],
    },
    install_requires=[
        #
        # data science
        'numpy',
        'pandas',
        'pandas-stubs',
        #
        # data dependencies
        'aiohttp',
        'aiofiles',
        'pyyaml',
        'toml',
        #
        # tool suite
        'toolcache',
        'toolcli>=0.3.8',
        'toolconf',
        'toolsql>=0.2.2',
        'toolstr>=0.1.3',
        'tooltable',
        'tooltime',
        #
        # EVM dependencies
        'pycryptodome',  # for keccak()
        'eth_abi',  # for encode_single()/decode_single()
        'idna',  # ENS resolution
        'eth_utils',  # for collapse_if_tuple()
        'rlp',  # for create2 address computation
    ],
    extras_require={
        'test': [
            'pytest',
            'pytest-asyncio',
        ],
        'performance': [
            'pysha3',  # for keccak()
            'scikit-image',  # for console unicode drawing with toolstr
            'orjson',  # for json loading
        ],
        'plots': [
            'matplotlib',
            'toolplot',
        ],
    },
    scripts=[
        './scripts/ctc',
    ],
)

