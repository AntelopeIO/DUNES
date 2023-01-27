@echo off

(where choco.exe)>nul 2>&1
if errorlevel 1 (
    echo Choco not installed. Installing now..
    @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
)

set mypath=%cd%
set script-path=%~dp0

set target-dir=%script-path%\antelopeio-dune\tools
mkdir %target-dir%
copy %script-path%\..\LICENSE %target-dir%
copy "%script-path%"\..\dune* %target-dir%
copy "%script-path%"\..\Dockerfile* %target-dir%
copy "%script-path%"\..\bootstrap* %target-dir%
copy "%script-path%"\..\README* %target-dir%

mkdir %target-dir%\src\
xcopy "%script-path%"\..\src\* %target-dir%\src /e /k /h /i
mkdir %target-dir%\scripts\
xcopy "%script-path%"\..\scripts\* %target-dir%\scripts\ /e /k /h /i
mkdir %target-dir%\tests\
xcopy "%script-path%"\..\tests\* %target-dir%\tests\ /e /k /h /i
del /f %target-dir%\tests\.gitignore
mkdir %target-dir%\plugin_example\
xcopy "%script-path%"\..\plugin_example\* %target-dir%\plugin_example\ /e /k /h /i
mkdir %target-dir%\docs\
xcopy "%script-path%"\..\docs\* %target-dir%\docs\ /e /k /h /i


cd %script-path%\antelopeio-dune

choco pack
cd %mypath%
rmdir /Q /S %target-dir%
move %script-path%\antelopeio-dune\*.nupkg %mypath%

echo Nupkg has been created in the current directory