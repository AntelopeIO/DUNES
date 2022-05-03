# syntax=docker/dockerfile:1
FROM ubuntu:20.04
RUN apt-get update
RUN apt-get update --fix-missing
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
RUN apt-get -y install zip unzip libncurses5 wget git build-essential cmake curl libboost-all-dev libcurl4-openssl-dev libgmp-dev libssl-dev libusb-1.0.0-dev libzstd-dev llvm-11-dev time pkg-config

WORKDIR /app
RUN git clone https://github.com/eosnetworkfoundation/mandel

# get CDT
RUN wget https://github.com/eosio/eosio.cdt/releases/download/v1.8.1/eosio.cdt_1.8.1-1-ubuntu-18.04_amd64.deb
RUN apt install ./eosio.cdt_1.8.1-1-ubuntu-18.04_amd64.deb

WORKDIR /app/mandel
RUN git submodule update --init --recursive

WORKDIR /app/build

RUN cmake ../mandel -DCMAKE_BUILD_TYPE=Release -DENABLE_OC=Off
RUN make -j4 && make install

WORKDIR /app

COPY ./scripts/* .
RUN chmod +x start_node.sh
RUN chmod +x setup_system.sh
RUN chmod +x write_context.sh
RUN mv my_init /sbin

RUN ./setup_system.sh

# thanks to github.com/phusion
# this should solve reaping issues of stopped nodes
CMD ["/sbin/my_init"]

# port for nodeos p2p
EXPOSE 9876
# port for nodeos http
EXPOSE 8888
# port for state history
EXPOSE 8080