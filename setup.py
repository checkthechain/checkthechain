import setuptools

setuptools.setup(
    name='fei',
    version='0.0.1',
    # packages=['fei', 'larp'],
    packages=setuptools.find_packages("./src"),
    package_dir={'': 'src'},
    install_requires=[
        'boto3',
        'matplotlib',
        'numpy',
        'pandas',
        # 'numba',
        'tooltime',
        'toolcache',
        'pyyaml',
        'requests',
    ],
)

