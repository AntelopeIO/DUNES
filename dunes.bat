@echo off

SET mypath=%~dp0

where python.exe >nul
if %ERRORLEVEL% EQU 0 (
  python %mypath%\src\dunes %*
  ) else (
  where python3.exe >nul
  if %ERRORLEVEL% EQU 0 (
    python3 %mypath%\src\dunes %*
  ) else (
    echo "Python/3 was not found, please install and add to PATH."
	exit /b
  )
)
