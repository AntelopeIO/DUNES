from docker import docker 

import os, sys, tempfile

class ctx:
   active    = "" # active node
   http_port = "" # active node's http port
   p2p_port  = "" # active node's p2p port
   ship_port = "" # active node's ship port 

class context:
   _file_name = ".dune.ctx"
   _dir       = '/home/www-data/'
   _docker    = None
   _ctx       = ctx()

   def __init__(self, dockr):
      self._docker = dockr
      if self._docker.file_exists(self._dir + self._file_name):
         self.read_ctx()
   
   def read_ctx(self):
      arr = self._docker.execute_cmd(['cat', self._dir + self._file_name])[0].splitlines()
      self._ctx.active    = arr[0]
      self._ctx.http_port = arr[1]
      self._ctx.p2p_port  = arr[2]
      self._ctx.ship_port = arr[3]
   
   def write_ctx(self):
      ctx_str = self._ctx.active + "\\n"
      ctx_str = ctx_str + self._ctx.http_port + "\\n"
      ctx_str = ctx_str + self._ctx.p2p_port + "\\n"
      ctx_str = ctx_str + self._ctx.ship_port
      stdout, stderr, ec = self._docker.execute_cmd(['/app/write_context.sh', ctx_str])
      print(stdout)
      print(stderr)
   
   def is_commented(self, s):
      for c in s:
         if c == '#':
            return True
         if c == ' ':
            continue
      return False

   def get_ctx(self):
      return self._ctx 
   def get_active(self):
      return self._ctx.active

   def get_config_args(self, n):
      conf, stderr, ec = self._docker.execute_cmd(['cat', '/home/www-data/nodes/'+n.name()+'/config.ini'])
      
      http_port = None
      p2p_port  = None
      ship_port = None

      for line in conf.splitlines():
         if not self.is_commented(line):
            if "http-server-address" in line:
               http_port = line.split('=')[1][1:]
            elif "p2p-listen-endpoint" in line:
               p2p_port = line.split('=')[1][1:]
            elif "state-history-endpoint" in line:
               ship_port = line.split('=')[1][1:]
      
      # if they don't exist just set to normal default values
      if http_port == None:
         http_port = "127.0.0.1:8888"
      if p2p_port == None:
         p2p_port = "0.0.0.0:9876"
      if ship_port == None:
         ship_port = "127.0.0.1:8080"
      return [http_port, p2p_port, ship_port]

   def set_active(self, n):
      self._ctx.active = n.name()
      self._ctx.http_port, self._ctx.p2p_port, self._ctx.ship_port = self.get_config_args(n)
      self.write_ctx()