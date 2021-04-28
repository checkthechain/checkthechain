import setuptools

setuptools.setup(
    name='fei',
    version='0.0.1',
    packages=['fei', 'larp'],
    install_requires=[
        'matplotlib',
        'numpy',
        'pandas',
        # 'numba',
        'tooltime',
    ],
)

