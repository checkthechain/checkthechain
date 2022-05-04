FROM ubuntu:22.04

# install system packages
RUN apt-get update -y
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y git

# create default user
RUN useradd -ms /bin/bash user

# install dependencies first for faster iterated build times

# install ctc
COPY . /home/user/repos/ctc/
RUN chown -R user /home/user/repos/ctc
USER user
WORKDIR /home/user/repos/ctc
RUN python3 -m pip install ./ --user

