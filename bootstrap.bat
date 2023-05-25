@echo off

SET mypath=%~dp0
docker build --no-cache -f Dockerfile.win -t dunes %mypath%
