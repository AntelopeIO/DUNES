# DUNE plugins

DUNE allows users to extend its functionality through the use of plugins. DUNE plugins are simply Python scripts which are fulfilling specific requirements explained below.

## Plugin requirements
1. Plugin needs to be placed in the subdirectory of [../src/plugin/](../src/plugin/).
2. In the aforementioned subdirectory you need to create script `main.py`.
3. `main.py` needs to define 3 functions:
   1. `add_parsing(parser)` - function that receives instance of [argparse.ArgumentParser](https://docs.python.org/3/library/argparse.html). It is used to add new DUNE command parsing arguments.
   2. `handle_args(args)` - function that receives populated namespace returned by [ArgumentParser.parse_args](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.parse_args). It is used to handle new DUNE command arguments.
   3. (optionally) `set_dune(dune)` - function that receives instance of DUNE so the user could interact with DUNE. It might be stored for later usage if needed.

## Plugin examples
You can find example plugins in [plugin_example directory](../plugin_example/).
To test the example plugins, copy the contents of the [../plugin_example/](../plugin_example) directory into the [../src/plugin/](../src/plugin/) directory. This way, DUNE will automatically discover the new plugins.

### dune_hello
The simplest plugin, which adds `--hello` to DUNE commands. When command `dune --hello` is executed then an example output is printed.

### account_setup
Plugin adds command `--bootstrap-account` to DUNE commands. When it is executed 3 example accounts are created: `alice`, `bob` and `cindy`.
Additionally the contract `eosio.token` is deployed to all above accounts.

In this example you can see how `set_dune` function is being used to store `dune` instance and later use it to create and prepare accounts.