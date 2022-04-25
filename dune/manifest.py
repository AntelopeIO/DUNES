from utilities import docker 
from utilities import node

import os, sys

class manifest:
   _file_name = ".dune.manifest"
   _dir       = '/app/dune/'
   _dockr     = docker()
   def __init__(self):
      if self._dockr.file_exists(self._dir + self._file_name):
         print("Found file")
      self._dockr.execute_cmd(['mkdir', '-p', self._dir])
      self._dockr.execute_cmd(['touch', self._dir + self._file_name])
   
   def read_manifest(self):
      f, stderr, ec = self._dockr.execute_cmd(['cat', self._dir + self._file_name])
      print(f)

   def add_node(self, n):
      stdout, stderr, ec = self._dockr.execute_cmd(['echo', n.name(), '>>', self._dir+self._file_name])