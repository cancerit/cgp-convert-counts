FROM ubuntu:18.04

LABEL maintainer="cgphelp@sanger.ac.uk" \
      uk.ac.sanger.cgp="Cancer, Ageing and Somatic Mutation, Wellcome Trust Sanger Institute" \
      version="0.1.4" \
      description="cgp-convert-counts container"

RUN apt-get -yq update
RUN apt-get install -yq --no-install-recommends \
    ca-certificates \
    curl \
    python3.7 python3.7-distutils \
    unattended-upgrades && \
    unattended-upgrade -d -v && \
    apt-get remove -yq unattended-upgrades && \
    apt-get autoremove -yq && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1

# install pip3
RUN curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3 get-pip.py --prefix=/usr/local/ && rm -f get-pip.py

# install dependency packages
COPY requirements.txt .
RUN pip3 install -r requirements.txt && rm requirements.txt

# setting up the final user
ENV USER casm
ENV HOME /home/casm
ENV OPT /opt/casm
ENV PATH $OPT/bin:$PATH
RUN adduser --disabled-password --shell /bin/bash --gecos '' $USER

# copy python scripts to $HOME
COPY scripts/*.py $OPT/bin/

# become the user
USER casm
WORKDIR $HOME
