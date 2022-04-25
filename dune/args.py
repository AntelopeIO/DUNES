import argparse

class arg_parser:
   def __init__(self):
      self._parser = argparse.ArgumentParser(description='DUNE: Docker Utilities for Node Execution')
      self._parser.add_argument('--start', metavar="NODE", help='start a new node with a given name')
      self._parser.add_argument('--stop', metavar="NODE", help='stop a node with a given name')
      self._parser.add_argument('--remove', metavar="NODE", help='a node with a given name, will stop the node if running')
      self._parser.add_argument('--export-node', metavar=("NODE", "DIR"), nargs=2, help='export state and blocks log for the given node.')
      self._parser.add_argument('--import-node', metavar=("DIR", "NODE"), nargs=2, help='import state and blocks log to a given node')
      self._parser.add_argument('--destroy-container', action='store_true', help='destroy context container <Warning, this will destroy your state and block log>')
      self._parser.add_argument('--producer', metavar=("NAME"), help='producer name for node')
      self._parser.add_argument('--api', action='store_true', help='flag to create a non-producing node')
      self._parser.add_argument('--raw-nodeos', metavar="CMD", help='send commands directly to nodeos')
      self._parser.add_argument('--raw-cleos', metavar="CMD", help='send commands directly to cleos')
      self._parser.add_argument('--monitor', metavar="NODE", help='view stdout for a node with the given name')

   def parse(self):
      return self._parser.parse_args()