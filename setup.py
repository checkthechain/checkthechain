import setuptools


setuptools.setup(
    name='checkthechain',
    version='0.2.9',
    packages=setuptools.find_packages("./src"),
    package_dir={'': 'src'},
    package_data={'ctc': ['default_data/*']},
    install_requires=[
        #
        # data science
        'matplotlib',
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
        'toolcli>=0.3.4',
        'toolconf',
        'toolplot',
        'toolstr>=0.1.2',
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
        'speed': [
            'pysha3',  # for keccak()
        ],
    },
    scripts=[
        './scripts/ctc',
    ],
)

