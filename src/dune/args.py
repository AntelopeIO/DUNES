import argparse
import sys


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
        return cmd[1:]  # remove leading --
    return cmd  # empty list


class arg_parser:

    def __init__(self):
        self._parser = argparse.ArgumentParser(
            description='''DUNE: Docker Utilities for Node Execution.
                        -- [COMMANDS] run any number of commands in the container.
                        Example: dune -- cleos --help''')
        self._parser.add_argument('-s', '--start', nargs=1, metavar=("NODE"),
                                  help='start a new node with a given name')
        self._parser.add_argument('-c', '--config', nargs=1, metavar=("CONFIG_DIR"),
                                  help='optionally used with --start, a path containing'
                                  ' the config.ini file to use')
        self._parser.add_argument(
            '--stop', metavar="NODE", help='stop a node with a given name')
        self._parser.add_argument('--remove', metavar="NODE",
                                  help='a node with a given name, will stop the node if running')
        self._parser.add_argument('--list', action='store_true',
                                  help='list all nodes available and their statuses')
        self._parser.add_argument('--simple-list', action='store_true',
                                  help='list all nodes available and their statuses without '
                                       'formatting and unicode')
        self._parser.add_argument('--set-active', metavar="NODE",
                                  help='set a node to active status')
        self._parser.add_argument('--get-active', action='store_true',
                                  help='get the name of the node that is currently active')
        self._parser.add_argument('--export-node', metavar=("NODE", "PATH"), nargs=2,
                                  help='export state and blocks log for the given node. '
                                  'PATH may be a directory or a filename with `.tgz` extension.')
        self._parser.add_argument('--import-node', metavar=("NODE", "PATH"), nargs=2,
                                  help='import state and blocks log to a given node'
                                  'PATH *must* be a previously exported node ending in `.tgz`.')
        self._parser.add_argument('--monitor', action='store_true',
                                  help='monitor the currently active node')
        self._parser.add_argument('--import-dev-key', metavar="KEY",
                                  help='import a private key into developement wallet')
        self._parser.add_argument('--create-key', action='store_true',
                                  help='create an public key private key pair')
        self._parser.add_argument('--export-wallet', action='store_true',
                                  help='export the internal development wallet')
        self._parser.add_argument('--import-wallet', metavar="DIR",
                                  help='import a development wallet')
        self._parser.add_argument('--create-account', nargs='+',
                                  metavar=["NAME", "CREATOR (Optional)", "PUB_KEY (Optional)",
                                           "PRIV_KEY (Optional)"],
                                  help='create an EOSIO account and an optional creator (the '
                                       'default is eosio)')
        self._parser.add_argument('--create-cmake-app', nargs=2, metavar=["PROJ_NAME", "DIR"],
                                  help='create a smart contract project at from a specific host '
                                       'location')
        self._parser.add_argument('--create-bare-app', nargs=2, metavar=["PROJ_NAME", "DIR"],
                                  help='create a smart contract project at from a specific host '
                                       'location')
        self._parser.add_argument('--cmake-build', nargs=1, metavar=["DIR", "-- FLAGS (Optional)"],
                                  help='build a smart contract project at the directory given '
                                       'optional flags are of the form -- -DFLAG1=On '
                                       '-DFLAG2=Off]')
        self._parser.add_argument('--ctest', nargs=1, metavar=["DIR", "-- FLAGS (Optional)"],
                                  help='run the ctest tests for a smart contract project at the '
                                       'directory given. Optional flags are of the form -- -VV')
        self._parser.add_argument('--gdb', nargs=1, metavar=["PROGRAM", "-- FLAGS (Optional)"],
                                  help='start gdb into the container with given executive binary'
                                       'Optional flags are of the form -- -VV')
        self._parser.add_argument('--deploy', nargs=2, metavar=["DIR", "ACCOUNT"],
                                  help='deploy a smart contract and ABI to account given')
        self._parser.add_argument('--destroy-container', action='store_true',
                                  help='destroy context container <Warning, this will destroy '
                                       'your state and block log>')
        self._parser.add_argument('--stop-container', action='store_true',
                                  help='stop the context container')
        self._parser.add_argument('--start-container', action='store_true',
                                  help='start the context container')
        self._parser.add_argument('--set-core-contract', metavar="ACCOUNT",
                                  help='set the core contract to an account given (default '
                                       'normally is `eosio`)')
        self._parser.add_argument('--set-bios-contract', metavar="ACCOUNT",
                                  help='set the bios contract to an account given (default '
                                       'normally is `eosio`)')
        self._parser.add_argument('--set-token-contract', metavar="ACCOUNT",
                                  help='set the token contract to an account given (default '
                                       'normally is`eosio.token`)')
        self._parser.add_argument('--bootstrap-system', action='store_true',
                                  help='install boot contract to eosio and activate all protocol '
                                       'features')
        self._parser.add_argument('--bootstrap-system-full', action='store_true',
                                  help='same as `--bootstrap-system` but also creates accounts '
                                       'needed for core contract and deploys core, token, '
                                       'and multisig contracts')
        self._parser.add_argument('--send-action', nargs=4, action=fix_action_data,
                                  metavar=["ACCOUNT", "ACTION", "DATA", "PERMISSION"],
                                  help='send action to account with data given and permission')
        self._parser.add_argument('--get-table', nargs=3, metavar=["ACCOUNT", "SCOPE", "TABLE"],
                                  help='get the data from the given table')
        self._parser.add_argument('--activate-feature', metavar="CODENAME",
                                  help='active protocol feature')
        self._parser.add_argument('--list-features', action='store_true',
                                  help='list available protocol feature code names')
        self._parser.add_argument('--version', action='store_true',
                                  help='display the current version of DUNE')
        self._parser.add_argument('--version-all', action='store_true',
                                  help='display the current version of DUNE, CDT and leap')
        self._parser.add_argument('--debug', action='store_true', help='print additional info '
                                                                       'useful for debugging, '
                                                                       'like running docker '
                                                                       'commands')
        self._parser.add_argument(
            '--upgrade', action='store_true', help='upgrades DUNE image to the latest version')
        self._parser.add_argument(
            '--leap', metavar="LEAP_VERSION", help='sets the version of leap')
        self._parser.add_argument('--cdt', metavar="CDT_VERSION", help='sets the version of CDT (Contract '
                                  'Development Toolkit)')
        # used to store arguments to individual programs, starting with --
        self._parser.add_argument('remainder',
                                  nargs=argparse.REMAINDER)
        # pylint: disable=fixme
        # TODO readdress after the launch
        # self._parser.add_argument('--start-webapp', metavar=["DIR"], help='start a webapp with ')

    @staticmethod
    def is_forwarding():
        return len(sys.argv) > 1 and sys.argv[1] == '--'

    @staticmethod
    def get_forwarded_args():
        return sys.argv[2:]

    def parse(self):
        return self._parser.parse_args()

    def exit_with_help_message(self, *args, return_value=1):
        self._parser.print_help(sys.stderr)
        print("\nError: ", *args, file=sys.stderr)
        sys.exit(return_value)
