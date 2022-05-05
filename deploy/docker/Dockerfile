FROM ubuntu:22.04

# force non-interactive installations
ENV DEBIAN_FRONTEND noninteractive

# install system packages
RUN apt-get update -y
RUN apt install -y \
    software-properties-common \
    curl

# install python
RUN add-apt-repository ppa:deadsnakes/ppa
ARG PYTHON_VERSION=python3.7
RUN apt-get install -y \
    build-essential \
    ${PYTHON_VERSION} \
    ${PYTHON_VERSION}-dev \
    ${PYTHON_VERSION}-distutils
RUN curl https://bootstrap.pypa.io/get-pip.py | ${PYTHON_VERSION}

# create default user
RUN useradd -ms /bin/bash user
USER user

# install dependencies first for faster iterated build times
RUN ${PYTHON_VERSION} -m pip install \
    "toolcli>=0.3.8" \
    "toolsql>=0.2.3" \
    "toolstr>=0.1.3" \
    aiofiles \
    aiohttp \
    eth_abi \
    eth_utils \
    idna \
    numpy --user \
    pandas \
    pandas-stubs \
    pycryptodome \
    pyyaml \
    rlp \
    toml \
    toolcache \
    toolconf \
    tooltable \
    tooltime \
    --user

# install ctc
COPY . /home/user/repos/ctc/
USER root
RUN chown -R user /home/user/repos/ctc
USER user
WORKDIR /home/user/repos/ctc
RUN ${PYTHON_VERSION} -m pip install ./ --user
RUN echo 'PATH="~/.local/bin":$PATH' >.bashrc

