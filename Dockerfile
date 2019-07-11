FROM python:3.7.4-alpine3.10

# Add service user
ENV USER=casm
ENV HOME=/opt/casm
RUN mkdir -p $HOME
RUN addgroup $USER && \
    adduser -G $USER -D -h $HOME $USER

# copy the script to $HOME

WORKDIR $HOME
