$ErrorActionPreference = 'Stop'; # stop on all errors

$toolsDir = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"

Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment' -Name Path -Value "$toolsDir;$($env:Path)"

python -m pip install --exists-action i --disable-pip-version-check -r $toolsDir/requirements.txt
