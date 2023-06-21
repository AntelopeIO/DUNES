#! /usr/bin/env bash

if [ "$#" -ne 2 ]; then
   echo "Usage: $0 system_type (macos, linux, windows) src_path"
   exit
fi

if [ "$1" == "macos" ]; then
   echo "Installing DUNES on MacOS"
   python3 $2/bootstrap.py
   python3 $2/packaging/ext.py --specpath $2 --src $2 --layout macos
elif [ "$1" == "linux" ]; then
   echo "Creating Linux package"
   python3 $2/packaging/ext.py --specpath $2 --src $2 --layout linux
elif [ "$1" == "windows" ]; then
   echo "Creating Windows package"
   python3 $2/packaging/ext.py --specpath $2 --src $2 --layout win
else
   echo "Usage: $0 system_type (macos, linux, windows) src_path"
   exit
fi
