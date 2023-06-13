# syntax=docker/dockerfile:1
FROM ubuntu:20.04

ARG USER_ID
ARG GROUP_ID

ARG ORG="AntelopeIO"

# The following tool versions should be updated to match the latest release. Note that contracts currently takes the full git commit hash.
ARG LEAP_VERSION=4.0.1
ARG CDT_VERSION=4.0.0
ARG CONTRACTS_VERSION=76197b4bc60d8dc91a5d65ecdbf0f785e982e279


RUN apt-get update
RUN apt-get update --fix-missing
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
RUN apt-get -y install zip unzip libncurses5 wget git build-essential cmake curl libboost-all-dev libcurl4-openssl-dev libgmp-dev libssl-dev libusb-1.0.0-dev libzstd-dev time pkg-config llvm-11-dev nginx npm yarn jq gdb lldb
RUN npm install -D webpack-cli
RUN npm install -D webpack
RUN npm install -D webpack-dev-server

WORKDIR /app

# Copy the scripts
COPY ./scripts/ .
RUN chmod +x *.sh
RUN mv my_init /sbin

# Install our software.
RUN ./bootstrap_leap.sh $LEAP_VERSION
RUN ./bootstrap_cdt.sh $CDT_VERSION
RUN ./bootstrap_contracts.sh $CONTRACTS_VERSION
RUN ./setup_system.sh

RUN mkdir -p /app/nodes

# thanks to github.com/phusion
# this should solve reaping issues of stopped nodes
CMD ["/sbin/my_init"]

# port for nodeos p2p
EXPOSE 9876
# port for nodeos http
EXPOSE 8888
# port for state history
EXPOSE 8080
# port for webapp
EXPOSE 8000
