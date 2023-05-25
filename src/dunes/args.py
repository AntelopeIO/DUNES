import argparse
import sys
import argcomplete


class fix_action_data(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        fixed_list = [values[0], values[1], values[2].strip(), values[3]]
        setattr(namespace, self.dest, fixed_list)


def fix_args(args):
    arg_list = []
    arg_so_far = ""
    state = False
    for arg in args:
        if not state:
            if arg.startswith('['):
                state = True
                arg_so_far = arg[1:]
                continue
            arg_list.append(arg)
            continue
        if state:
            if arg.endswith(']'):
                arg_so_far = arg_so_far + arg[:-1]
                state = False
                arg_list.append(arg_so_far)
                arg_so_far = ""
                continue
            arg_so_far = arg_so_far + arg

    return arg_list


def parse_optional(cmd):
    if cmd is not None:
        return cmd[1:], cmd != []  # remove leading --
    return cmd, cmd != []  # empty list


class arg_parser:

    def __init__(self):
        self._parser = argparse.ArgumentParser(
            description='''DUNES: Docker Utilities for Node Execution and Subsystems.
                    dunes [ARGUMENTS] -- <COMMANDS> runs any number of commandline commands in the container.
                    Example: dunes -- cleos --help''')
        self._parser.add_argument('-s', '--start', nargs=1, metavar="<NODE>",
                                  help='start a new node with a given name.')
        self._parser.add_argument('-c', '--config', nargs=1, metavar="<CONFIG_DIR>",
                                  help='optionally used with --start, a path containing'
                                  ' the config.ini file to use.')
        self._parser.add_argument(
            '--stop', metavar="NODE", help='stop a node with a given name.')
        self._parser.add_argument('--remove', metavar="<NODE>",
                                  help='Remove a node with a given name. '
                                       'If the node is running it will be stopped.')
        self._parser.add_argument('--list', action='store_true',
                                  help='Print list of all available nodes and their status.')
        self._parser.add_argument('--simple-list', action='store_true',
                                  help='Print the same as --list but without formatting.')
        self._parser.add_argument('--set-active', metavar="<NODE>",
                                  help='Make the given node active.')
        self._parser.add_argument('--get-active', action='store_true',
                                  help='Print name of the active node.')
        self._parser.add_argument('--export-node', metavar=("<NODE>", "<PATH>"), nargs=2,
                                  help="Export state and blocks log of the given node. "
                                       "PATH may be a directory or a filename with `.tgz` extension.")
        self._parser.add_argument('--import-node', metavar=("<NODE>", "<PATH>"), nargs=2,
                                  help='Import state and blocks log to a given node. '
                                  'PATH *must* be a path to a file which contains previously '
                                       'exported node with `.tgz` extension.')
        self._parser.add_argument('--monitor', action='store_true',
                                  help='Monitor the currently active node.')
        self._parser.add_argument('--import-dev-key', metavar="<KEY>",
                                  help='Import a private key into development wallet.')
        self._parser.add_argument('--create-key', action='store_true',
                                  help='Create a public key - private key pair.')
        self._parser.add_argument('--export-wallet', action='store_true',
                                  help='Export the development wallet.')
        self._parser.add_argument('--import-wallet', metavar="<DIR>",
                                  help='Import the development wallet.')
        self._parser.add_argument('--create-account', nargs='+',
                                  metavar='',
                                  help='<NAME> [CREATOR] [PUB_KEY] [PRIV_KEY] [-- OPTIONS] '
                                       'Create an EOSIO account and an optional creator (the '
                                       'default is eosio). See `man dunes` for details.')
        self._parser.add_argument('--system-newaccount', nargs='+',
                                  metavar='',
                                  help='<NAME> [CREATOR] [PUB_KEY] [PRIV_KEY] [-- OPTIONS] '
                                       'Create an EOSIO account with initial resources using '
                                       '"cleos system newaccount" command. See `man dunes` for details. '
                                       'Example of the option: "-- --buy-ram-bytes 3000"')
        self._parser.add_argument('--create-cmake-app', nargs=2, metavar=("<PROJ_NAME>", "<DIR>"),
                                  help='Create a new empty smart contract project at the given location.')
        self._parser.add_argument('--create-bare-app', nargs=2, metavar=("<PROJ_NAME>", "<DIR>"),
                                  help='create a smart contract project at from a specific host location')
        self._parser.add_argument('--cmake-build', nargs=1, metavar="<DIR>",
                                  help='[-- OPTIONS] Build a smart contract project at the given directory. '
                                       'Additional CMake options can be added to CMake call as OPTIONS '
                                       'See `man dunes` for details.')
        self._parser.add_argument('--ctest', nargs=1, metavar="<DIR>",
                                  help='[-- OPTIONS] Run the ctest tests for a smart contract project '
                                       'at the directory given. '
                                       'Additional ctest options can be added to ctest call as OPTIONS')
        self._parser.add_argument('--gdb', nargs=1, metavar="<PROGRAM>",
                                  help='[-- OPTIONS] Start gdb in the container with given executive binary. '
                                       'Additional gdb options can be added to the call as OPTIONS')
        self._parser.add_argument('--deploy', nargs=2, metavar=("<DIR>", "<ACCOUNT>"),
                                  help='Deploy a smart contract to a given account.')
        self._parser.add_argument('--destroy-container', action='store_true',
                                  help='Destroy the current Docker container. '
                                       'Warning! This will destroy your state and block log. ')
        self._parser.add_argument('--stop-container', action='store_true',
                                  help='Stop the current Docker container.')
        self._parser.add_argument('--start-container', action='store_true',
                                  help='Start the current Docker container.')
        self._parser.add_argument('--set-core-contract', metavar="<ACCOUNT>",
                                  help='Set the core contract to the specified account '
                                       '(use `eosio` as account for normal system setup).')
        self._parser.add_argument('--set-bios-contract', metavar="<ACCOUNT>",
                                  help='Set the BIOS contract to the specified account '
                                       '(use `eosio` as account for normal system setup).')
        self._parser.add_argument('--set-token-contract', metavar="<ACCOUNT>",
                                  help='Set the token contract to the specified account '
                                       '(use `eosio.token` as account for normal system setup).')
        self._parser.add_argument('--bootstrap-system', action='store_true',
                                  help='Do setup of typical configuration settings to prepare EOS system '
                                       'for work. '
                                       'Install boot contracts to eosio and activate all protocol features.')
        self._parser.add_argument('--bootstrap-system-full',
                                  nargs='*',  metavar='',
                                  help='[CURRENCY] [MAX_VALUE] [INITIAL_VALUE] '
                                       'Do the same as `--bootstrap-system` but also creates accounts '
                                       'for core contract and deploys the core, token, '
                                       'and multisig contracts. If optional arguments are provided '
                                       'it creates specific CURRENCY (default "SYS") with maximum amount of '
                                       'MAX_VALUE and initial value of INITIAL_VALUE')
        self._parser.add_argument('--send-action', nargs=4, action=fix_action_data,
                                  metavar=("<ACCOUNT>", "<ACTION>", "<DATA>", "<PERMISSION>"),
                                  help='Send an action to a specified account with given data and permission.')
        self._parser.add_argument('--get-table', nargs=3, metavar=("<ACCOUNT>", "<SCOPE>", "<TABLE>"),
                                  help='Print data from a given table.')
        self._parser.add_argument('--activate-feature', nargs=1, metavar="<CODENAME>",
                                  help='Activate a given protocol feature.')
        self._parser.add_argument('--list-features', action='store_true',
                                  help='Print a list of available protocol features.')
        self._parser.add_argument('--version', action='store_true',
                                  help='Display the current version of DUNES.')
        self._parser.add_argument('--version-all', action='store_true',
                                  help='Display the current versions of DUNES, CDT, and leap.')
        self._parser.add_argument('--version-short', action='store_true', help=argparse.SUPPRESS)
        self._parser.add_argument('--debug', action='store_true',
                                  help='Print additional information useful for debugging, '
                                       'such as running docker commands.')
        self._parser.add_argument(
            '--upgrade', action='store_true', help='Upgrade DUNES image to the latest version.')
        self._parser.add_argument(
            '--leap', nargs='?', const='-1', metavar="LEAP_VERSION",  help='Set the version of leap. '
            'If no version is provided, display available leap versions.')
        self._parser.add_argument('--cdt', nargs='?', const='-1', metavar="CDT_VERSION",
                                  help='Set the version of CDT (Contract Development Toolkit).'            
                                       'If no version is provided, display available CDT versions.')
        self.add_antler_arguments()

        # used to store arguments to individual programs, starting with --
        self._parser.add_argument('remainder',
                                  nargs=argparse.REMAINDER)
        # pylint: disable=fixme
        # TODO readdress after the launch
        # self._parser.add_argument('--start-webapp', metavar=["DIR"], help='start a webapp with ')

    def add_antler_arguments(self):
        self._parser.add_argument('--create-project', nargs="+", metavar='',
                                  help="<PROJ_NAME> <DIR> [VER] "
                                       "Create a smart contract project at the specified location.")

        self._parser.add_argument('--add-app', nargs="+",
                                  metavar='',
                                  help="<PROJ_DIR> <APP_NAME> <LANG> [CMPLR_OPTS] [LINK_OPTS] "
                                       "Add an application to the specified smart contract project.")
        self._parser.add_argument('--add-lib', nargs="+",
                                  metavar='',
                                  help="<PROJ_DIR> <LIB_NAME> <LANG> [CMPLR_OPTS] [LINK_OPTS] "
                                       "Add a library to the specified smart contract project.")
        self._parser.add_argument('--add-dep', nargs="+",
                                  metavar='',
                                  help="<PROJ_DIR> <OBJ_NAME> <DEP_NAME> [LOCATION] [TAG/RELEASE] [HASH] "
                                       "Add a dependency to the specified smart contract project.")

        self._parser.add_argument('--remove-app', nargs=2, metavar=("<PROJ_DIR>", "<APP_NAME>"),
                                  help='Remove an application from the specified smart contract project.')
        self._parser.add_argument('--remove-lib', nargs=2, metavar=("<PROJ_DIR>", "<LIB_NAME>"),
                                  help='Remove a library from the specified smart contract project.')
        self._parser.add_argument('--remove-dep', nargs=3, metavar=("<PROJ_DIR>", "<OBJ_NAME>", "<DEP_NAME>"),
                                  help='Remove a dependency from the specified smart contract project.')

        self._parser.add_argument('--update-app', nargs="+",
                                  metavar='',
                                  help='<PROJ_DIR> <APP_NAME> <LANG> [CMPLR_OPTS] [LINK_OPTS] '
                                       'Update an application in the specified smart contract project.')
        self._parser.add_argument('--update-lib', nargs="+",
                                  metavar='',
                                  help='<PROJ_DIR> <LIB_NAME> <LANG> [CMPLR_OPTS] [LINK_OPTS] '
                                       'Update a library in the specified smart contract project.')
        self._parser.add_argument('--update-dep', nargs="+",
                                  metavar='',
                                  help="<PROJ_DIR> <OBJ_NAME> <DEP_NAME> [LOCATION] [TAG/RELEASE] [HASH]"
                                       " Update a dependency in the specified smart contract project.")

        self._parser.add_argument('--build-project', nargs=1, metavar="<PROJ_DIR>",
                                  help='Build the specified smart contract project.')
        self._parser.add_argument('--clean-build-project', nargs=1, metavar="<PROJ_DIR>",
                                  help='Clean the specified project and rebuild it from scratch.')
        self._parser.add_argument('--validate', nargs=1, metavar="<PROJ_DIR>",
                                  help='Validate the specified smart contract project.')
        self._parser.add_argument('--populate', nargs=1, metavar="<PROJ_DIR>",
                                  help='Populate the specified smart contract project.')

    @staticmethod
    def is_forwarding():
        return len(sys.argv) > 1 and sys.argv[1] == '--'

    @staticmethod
    def get_forwarded_args():
        return sys.argv[2:]

    def parse(self):
        try:
            argcomplete.autocomplete(self._parser)
        except ImportError:
            print('Cannot load argcomplete. DUNES will work without autocompletion.')

        return self._parser.parse_args()

    def get_parser(self):
        return self._parser

    def exit_with_help_message(self, *args, return_value=1):
        self._parser.print_help(sys.stderr)
        print("\nError: ", *args, file=sys.stderr)
        sys.exit(return_value)
