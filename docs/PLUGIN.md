# DUNES plugins

DUNES allows users to extend its functionality through the use of plugins. DUNES plugins are simply Python scripts which are fulfilling specific requirements explained below.

## Plugin requirements
1. Plugin needs to be placed in the subdirectory of [../src/plugin/](../src/plugin/).
2. In the aforementioned subdirectory you need to create script `main.py`.
3. `main.py` needs to define 3 functions:
   1. `add_parsing(parser)` - function that receives instance of [argparse.ArgumentParser](https://docs.python.org/3/library/argparse.html). It is used to add new DUNES command parsing arguments.
   2.  (optionally) `set_dune(dune)` - function that receives instance of DUNES so the user could interact with DUNES. It might be stored for later usage if needed.
   3. `handle_args(args)` - function that receives populated namespace returned by [ArgumentParser.parse_args](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.parse_args). It is used to handle new DUNES command arguments.
   

## Plugin examples
You can find example plugins in [plugin_example directory](../plugin_example/).
To test the example plugins, copy or symbolically link the contents of the [../plugin_example/](../plugin_example) directory into the [../src/plugin/](../src/plugin/) directory. This way, DUNES will automatically discover the new plugins.

### dune_hello
The simplest plugin, which adds `--hello` to DUNES commands. When command `dunes --hello` is executed then an example output is printed.

### account_setup
Plugin adds command `--bootstrap-account` to DUNES commands. When it is executed 3 example accounts are created: `alice`, `bob` and `cindy`.
Additionally the contract `eosio.token` is deployed to all above accounts.

In this example you can see how `set_dune` function is being used to store `dune` instance and later use it to create and prepare accounts.

## Implementation details
DUNES starts with auto-discovering the plugins in the `src/plugin` subdirectories and dynamically loading each `main.py` file. The functions from each plugin are then called in the following order:
1. `add_parsing(parser)` - this function is called first to add parsing arguments. Users can also initialize their plugin at this stage, however, it should be noted that at this point it is not known if the plugin will be used.
2. (optionally) `set_dune(dune)` - if the user wants to interact with DUNES, they should store the DUNES object in this function.
3. `handle_args(args)` - the user should check if their parsing arguments are being used and handle them in this function. This is the main function where the plugin does its job. The DUNES object is usually needed in this function.
