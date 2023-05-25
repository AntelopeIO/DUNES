$ErrorActionPreference = 'Stop'; # stop on all errors

$currentPath = $env:Path

$toolsDir = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"

$escapedDirectory = [regex]::Escape($toolsDir)

$newPath = $currentPath -replace $escapedDirectory,''

Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment' -Name Path -Value $newPath