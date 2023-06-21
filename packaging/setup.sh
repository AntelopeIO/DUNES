#! /usr/bin/env bash

sudo apt install python3-pip
pip3 install --user pyinstaller
pip3 install --user argcomplete
pip3 install --user requests
pip3 install --user wget

export PATH=$PATH:~/.local/bin