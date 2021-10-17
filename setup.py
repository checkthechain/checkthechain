import setuptools

setuptools.setup(
    name='fei',
    version='0.0.1',
    # packages=['fei', 'larp'],
    packages=setuptools.find_packages("./src"),
    package_dir={'': 'src'},
    install_requires=[
        'boto3',
        'fsspec',
        's3fs',
        'matplotlib',
        'numpy',
        'pandas',
        'tooltime',
        'toolcache',
        'pyyaml',
        'requests',
    ],
)

