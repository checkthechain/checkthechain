import setuptools

setuptools.setup(
    name='fei',
    version='0.0.1',
    packages=['fei', 'larp'],
    package_dir={'': 'src'},
    install_requires=[
        'matplotlib',
        'numpy',
        'pandas',
        # 'numba',
        'tooltime',
    ],
)

