---
title: DUNES
section: 1
header: Docker Utilities for Node Execution and Subsystems
footer: AntelopeIO
date: April 04, 2023
---
# NAME
DUNES - Docker Utilities for Node Execution.

# SYNOPSIS

`dunes <option> [<arguments>] [-- <commands>]`

# DESCRIPTION

**DUNES** is a tool to abstract over Leap programs, CDT, and other services and tools to perform the functions 
of node management, compiling smart contracts, running tests, and other tasks required to develop smart 
contracts on Antelope blockchains. 

# OPTIONS

**`-- <COMMANDS>`** 

    Adding double dashes and space at the end of the command line appends trailing arguments to the current 
    command. If the current command is empty, trailing arguments are passed as though they are the command.

    Example: dunes -- cleos --help

**`-h, --help`** 

    Print the help message and exit

**`-s, --start <NODE>`** 

    Start a new node with a given name

**`-c <CONFIG_DIR>, --config <CONFIG_DIR>`**

    Optionally used with --start, a directory containing the config.ini file or the full path containing the .ini file to use.

**`--rmdirtydb`**

    Optionally used with --start to clean a database dirty flag of nodeos which was set likely due to unclean shutdown

**`--stop <NODE>`**

    Stop a node with a given name.

**`--remove <NODE>`**

    Remove a node with a given name. If the node is running it will be stopped.

**`--list`**

    Print list of all available nodes and their status.

**`--simple-list`**

    Print the same as --list but without formatting.

**`--set-active <NODE>`**

    Make the given node active.

**`--get-active`**

    Print name of the active node.

**`--export-node <NODE> <PATH>`**

    Export state and blocks log of the given node. PATH may be a directory or a filename with `.tgz` extension.
    
    Example: dunes --export-node node ~/storage/ 

**`--import-node <NODE> <PATH>`**

    Import state and blocks log to a given node. PATH *must* be a path to a file which contains previously exported 
    node with `.tgz` extension.
    
    Example: dunes --import-node node ~/storage/node.tgz`

**`--monitor`**

    Monitor the currently active node.

**`--import-dev-key <KEY>`**

    Import a private key into development wallet.

**`--create-key`**

    Create a public key - private key pair.

**`--export-wallet`**

    Export the development wallet.

**`--import-wallet <DIR>`**

    Import the development wallet.

**`--create-account <NAME> [CREATOR] [PUB_KEY] [PRIV_KEY] [-- OPTIONS]`**

    Create an EOSIO account and an optional creator (the default is eosio).
    This options calls cleos utility in the Docker container 
    so you may send additional cleos command line options to the call as OPTIONS

**`--system-newaccount <NAME> [CREATOR] [PUB_KEY] [PRIV_KEY] [-- OPTIONS]`**

    Create an EOSIO account with initial resources using "cleos system newaccount" command.
    This options calls cleos utility in the Docker container 
    so you may send additional cleos command line options to the call as OPTIONS

    Example: dunes --system-newaccount myaccount -- --buy-ram-bytes 3000
    
**`--create-cmake-app <PROJ_NAME> <DIR>`**

    Create a new smart contract project at the given location.

**`--create-bare-app <PROJ_NAME> <DIR>`**

    Create a new empty smart contract project at the given location.
     
**`--cmake-build <DIR> [-- OPTIONS]`**

    Build a smart contract project at the given directory.
    Additional CMake options can be added to CMake call as OPTIONS. 
     
    Example: dunes --cmake-build ~/project -- -DFLAG1=On -DFLAG2=Off               

**`--ctest <DIR> [-- OPTIONS]`**

    Run the ctest tests for a smart contract project at the directory given.
    Additional ctest options can be added to ctest call as OPTIONS.
     
    Example: dunes --ctest ~/project -- --progress -V

**`--gdb <PROGRAM> [-- OPTIONS]`**

    Start gdb in the container with given executive binary.
    Additional gdb options can be added to the call as OPTIONS.               

**`--deploy <DIR> <ACCOUNT>`**

    Deploy a smart contract to a given account.

**`--destroy-container`**

    Destroy the current Docker container. Warning! This will destroy your state and block log.

**`--stop-container`**

    Stop the current Docker container.

**`--start-container`**

    Start the current Docker container.


**`--set-core-contract <ACCOUNT>`**

    Set the core contract to the specified account (use `eosio` as account for normal system setup).

**`--set-bios-contract <ACCOUNT>`**

    Set the BIOS contract to the specified account (use `eosio` as account for normal system setup).

**`--set-token-contract <ACCOUNT>`**

    Set the token contract to the specified account (use `eosio.token` as account for normal system setup).

**`--bootstrap-system`**

    Do setup of typical configuration settings to prepare EOS system for work.
    Install boot contracts to eosio and activate all protocol features.

**`--bootstrap-system-full [CURRENCY] [MAX_VALUE] [INITIAL_VALUE]`**

    Do the same as `--bootstrap-system` but also creates accounts for core contracts and deploys 
    the core, token, and multisig contracts. 
    If optional arguments are provided, it creates specific CURRENCY (default "SYS") 
    with maximum amount of MAX_VALUE and initial value of INITIAL_VALUE.

**`--send-action <ACCOUNT> <ACTION> <DATA> <PERMISSION>`**

    Send an action to a specified account with given data and permission.

**`--get-table <ACCOUNT> <SCOPE> <TABLE>`**

    Print data from a given table.

**`--activate-feature <CODENAME>`**

    Activate a given protocol feature.

**`--list-features`**

    Print a list of available protocol features.

**`--version`**

    Display the current version of DUNES.

**`--version-all`**

    Display the current versions of DUNES, CDT, and leap.

**`--debug`**

    Print additional information useful for debugging, such as running docker commands.

**`--upgrade`**

    Upgrade DUNES image to the latest version.

**`--leap [LEAP_VERSION]`**

    Set the version of leap. If no version is provided, display available leap versions.

**`--cdt [CDT_VERSION]`**

    Set the version of CDT (Contract Development Toolkit). If no version is provided, display available CDT versions.

**`--create-project <PROJ_NAME> <DIR> [VER]`**

    Create a smart contract project at the specified location.

**`--add-app <PROJ_DIR> <APP_NAME> <LANG> [CMPLR_OPTS] [LINK_OPTS]`**

    Add an application to the specified smart contract project.

**`--add-lib <PROJ_DIR> <LIB_NAME> <LANG> [CMPLR_OPTS] [LINK_OPTS]`**

    Add a library to the specified smart contract project.

**`--add-dep <PROJ_DIR> <OBJ_NAME> <DEP_NAME> [LOCATION] [TAG/RELEASE] [HASH]`**

    Add a dependency to the specified smart contract project.

**`--remove-app <PROJ_DIR> <APP_NAME>`**

    Remove an application from the specified smart contract project.

**`--remove-lib <PROJ_DIR> <LIB_NAME>`**

    Remove a library from the specified smart contract project.

**`--remove-dep <PROJ_DIR> <OBJ_NAME> <DEP_NAME>`**

    Remove a dependency from the specified smart contract project.

**`--update-app <PROJ_DIR> <APP_NAME> <LANG> [CMPLR_OPTS] [LINK_OPTS]`**

    Update an application in the specified smart contract project.

**`--update-lib <PROJ_DIR> <LIB_NAME> <LANG> [CMPLR_OPTS] [LINK_OPTS]`**
 
    Update a library in the specified smart contract project.

**`--update-dep <PROJ_DIR> <OBJ_NAME> <DEP_NAME> [LOCATION] [TAG/RELEASE] [HASH]`**

    Update a dependency in the specified smart contract project.
 
**`--build-project <PROJ_DIR>`**

    Build the given smart contract project.
                        
**`--clean-build-project <PROJ_DIR>`**

    Clean the specified project and rebuild it from scratch.
                        
**`--validate <PROJ_DIR>`**

    Validate the specified smart contract project.
                        
**`--populate <PROJ_DIR>`**

    Populate the specified smart contract project.

# EXIT STATUS

**0** Success

**non-zero** Fail

# REPORTING BUGS

Please submit bug reports online at https://github.com/AntelopeIO/DUNES/issues

# SEE ALSO

**cdt**(1), **leap**(1)
  
#  COLOPHON

For more details consult the full documentation and sources https://github.com/AntelopeIO/DUNES