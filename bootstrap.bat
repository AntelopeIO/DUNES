@echo off

SET mypath=%~dp0
docker build --no-cache -t dune %mypath%