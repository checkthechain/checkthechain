# `ctc` Installation

- [Basic Installation](#basic-installation)
- [Upgrading](#upgrading)
- [Alternative Installations](#alternative-installations)
- [Python-devtools](#additional-dependencies)


## Basic Installation

Two steps:
1. `pip install checkthechain`
2. run `ctc setup` in terminal to specify data provider and data storage path

If your shell's `PATH` does not include python scripts you may need to do something like `python3 -m pip ...` and `python3 -m ctc ...`

Installation requires python3.7+


## Upgrading

Two steps:
1. `pip install checkthechain -U`
2. run `ctc setup` to add any new data to the data directory (can skip most steps by pressing enter)


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


## Additional Dependencies

In Ubuntu and Debian `build-essential` and `python-dev` are libraries required by many python packages including `ctc`. If you are an active python user you likely already have these installed, as they are required for many standard packages. If you are setting up a new machine or environment, you may need to install them according to your operating system and python version.

To install on Debian / Ubuntu can use the following:

```bash
PYTHON_VERSION=$(python3 -c "import sys; print('python' + str(sys.version_info.major) + '.' + str(sys.version_info.minor))")

python3 -m pip install $PYTHON_VERSION-dev
sudo apt-get install build-essential
```

