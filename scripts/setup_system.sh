#! /bin/sh

cleos wallet create --file .wallet.pw
cat .wallet.pw | cleos wallet unlock --password
# import main EOSIO account private key
cleos wallet import --private-key 5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3
