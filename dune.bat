@echo off

SET mypath=%~dp0

WHERE /q python3
IF ERRORLEVEL 1 (
   WHERE /q python
   IF ERRORLEVEL 1 (
      ECHO "Python/3 was not found, please install."
      EXIT /B
   ) ELSE (
      python %mypath%\src\dune %*
   )
) ELSE (
   python3 %mypath%\src\dune %*
)