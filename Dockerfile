# syntax=docker/dockerfile:1
FROM ubuntu:20.04

RUN apt-get update
RUN apt-get update --fix-missing
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
RUN apt-get -y install nginx npm yarn zip unzip libncurses5 wget git build-essential cmake curl libboost-all-dev libcurl4-openssl-dev libgmp-dev libssl-dev libusb-1.0.0-dev libzstd-dev llvm-11-dev time pkg-config
RUN npm install -D webpack-cli
RUN npm install -D webpack
RUN npm install -D webpack-dev-server

WORKDIR /app

# get Mandel
RUN wget https://github.com/larryk85/ENF-Binaries/releases/download/v1.0/mandel_3.0.5_amd64.deb
RUN apt install ./mandel_3.0.5_amd64.deb

# get CDT
RUN wget https://github.com/larryk85/ENF-Binaries/releases/download/v1.0/cdt_1.8.1_amd64.deb
RUN apt install ./cdt_1.8.1_amd64.deb

# get Contracts
RUN git clone https://github.com/eosnetworkfoundation/mandel-contracts 
WORKDIR /app/mandel-contracts
RUN git pull
RUN git checkout larryk85/mandel-update
RUN mkdir build
WORKDIR /app/mandel-contracts/build
RUN cmake ..
RUN make -j4

WORKDIR /app

COPY ./scripts/ .
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
# port for webapp
EXPOSE 8000
