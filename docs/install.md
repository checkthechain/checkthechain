
## Basic Installation

Two steps:
1. `pip install checkthechain`
2. run `ctc setup` in terminal to specify data provider and data storage path

If your shell's `PATH` does not include python scripts you may need to do something like `python3 -m pip ...` and `python3 -m ctc ...`

Installation requires python3.7+


## Alternative Installations

#### Installing from source

If you would like to install the latest version of `ctc` you can clone the repo directly:

```bash
git clone 
cd checkthechain
python -m pip install ./
```

#### Installing in Develop Mode / Edit Mode

If you would like to make edits to the `ctc` codebase and actively use those edits in your python programs, you can install the package in developer mode with the `-e` flag:

```bash
git clone 
cd checkthechain
python -m pip install ./
```


## Python Devtools

`python-dev` is a library required by many python packages including `ctc`. If you are an active python user, chances are you already have this installed, as this is a standard requirement for many packages. If you are a new python user, you may need to install it according to your operating system and python version.

To install on Debian / Ubuntu can use the following:

```bash
PYTHON_VERSION=$(python3 -c "import sys; print('python' + str(sys.version_info.major) + '.' + str(sys.version_info.minor))")

python3 -m pip install $PYTHON_VERSION-dev
```

