import argparse

class arg_parser:
   def __init__(self):
      self._parser = argparse.ArgumentParser(description='DUNE: Docker Utilities for Node Execution')
      self._parser.add_argument('--start', nargs='+', metavar=["NODE", "CONFIG-DIR (Optional)"], help='start a new node with a given name and an optional config.ini')
      self._parser.add_argument('--stop', metavar="NODE", help='stop a node with a given name')
      self._parser.add_argument('--remove', metavar="NODE", help='a node with a given name, will stop the node if running')
      self._parser.add_argument('--list', action='store_true', help='list all nodes available and their statuses')
      self._parser.add_argument('--set-active', metavar=("NODE"), help='set a node to active status')
      self._parser.add_argument('--get-active', action='store_true', help='get the name of the node that is currently active')
      self._parser.add_argument('--export-node', metavar=("NODE", "DIR"), nargs=2, help='export state and blocks log for the given node.')
      self._parser.add_argument('--import-node', metavar=("DIR", "NODE"), nargs=2, help='import state and blocks log to a given node')
      self._parser.add_argument('--raw-cmd', metavar="CMD", help='send commands directly to the container (cleos, nodeos, eosio-cpp, etc.)')
      self._parser.add_argument('--monitor', action='store_true', help='monitor the currently active node')
      self._parser.add_argument('--import-dev-key', metavar="KEY", help='import a private key into developement wallet')
      self._parser.add_argument('--create-key', action='store_true', help='create an public key private key pair')
      self._parser.add_argument('--create-account', nargs='+', metavar=["NAME","CREATOR (Optional)"], help='create an EOSIO account and an optional creator (the default is eosio)')
      self._parser.add_argument('--create-app-project', nargs='+', metavar=["PROJ_NAME", "DIR"], help='create a smart contract project at from a specific host location')
      self._parser.add_argument('--cmake-build', nargs='+', metavar=["DIR", "FLAGS (Optional)"], help='build a smart contract project at the directory given')
      self._parser.add_argument('--other-build', nargs='+', metavar=["DIR", "CMD", "FLAGS (Optional)"], help='build a smart contract project at the directory given')
      self._parser.add_argument('--destroy-container', action='store_true', help='destroy context container <Warning, this will destroy your state and block log>')
      self._parser.add_argument('--stop-container', action='store_true', help='stop the context container')

   def parse(self):
      return self._parser.parse_args()