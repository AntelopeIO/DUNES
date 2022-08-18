@echo off

SET mypath=%~dp0
docker build  -f Dockerfile.win -t dune %mypath%