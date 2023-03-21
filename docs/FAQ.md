- [How to pass JSON in PowerShell command to DUNE without escaping quotes?](#how-to-pass-json-in-powershell-command-to-dune-without-escaping-quotes)
- [How to retrieve a list of opened and closed wallets?](#how-to-retrieve-a-list-of-opened-and-closed-wallets)

<a name="json"></a>
## How to pass JSON in PowerShell command to DUNE without escaping quotes?

1. Download PowerShell version at least 7.3.
2. Run PowerShell 7 and type:
`$PSNativeCommandArgumentPassing = 'Standard'`
3. Now it is enough to surround your JSON with single quotes, i.e.
```
dune.bat -- cleos set account permission <ACCOUNT> active '{"threshold":1,"keys":[],"accounts":[{"permission":{"actor":"eosio.null","permission":"active"},"weight":1},{"permission":{"actor":"<ACCOUNT>","permission":"eosio.code"},"weight":1}],"waits":[]}' owner -p <ACCOUNT>
```

Solution based on https://stackoverflow.com/a/74440425.

On Linux in Bash it is enough to just simply use command from step 3 (with the difference of script name `dune` on Linux vs `dune.bat` on Windows).

<a name="wallets"></a>
## How to retrieve a list of opened and closed wallets?

By default command `cleos wallet list` lists only opened wallets. To find out the list of all the wallets you can try following command:
`dune -- ls /root/eosio-wallet/`