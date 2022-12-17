#!/usr/bin/env python3

"""
This file exists solely to allow for `show_untested_options.sh` to ignore certain keys.

These keys
  "--set-core-contract"
  "--set-bios-contract"
  "--set-token-contract"

are not tested because:

  Alex: I already do deployment of a contract and calling of
  it's action during test of --deploy key. Does it mean that all keys above don't need to be
  tested because actually they do deployment of contracts?

  Bucky: Yes, I think its fine to not worry about testing those specifically as they are just
  deploying contracts. When we get to creating the EOS specific plugin system we will have will
  need to validate the bootstrapping, but it will be more than deploying at that point.

"""
