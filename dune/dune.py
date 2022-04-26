from docker import docker
from context import context

class dune_error(Exception):
   pass
class dune_node_not_found(dune_error):
   _name = ""
   def __init__(self, n):
      self._name = n

   def name(self):
      return self._name


class node:
   _name = ""
   _cfg  = ""
   def __init__(self, nm, cfg = None):
      self._name = nm
      self._cfg = cfg
   
   def name(self):
      return self._name

   def config(self):
      return self._cfg
   
   def data_dir(self):
      return '/app/nodes/'+self.name()
   
   def config_dir(self):
      return '/app/nodes/'+self.name()

class dune:
   _docker    = None
   _wallet_pw = None
   _context   = None

   def __init__(self):
      self._docker = docker('dune_container', 'dune:latest')
      self._wallet_pw = self.get_wallet_pw()
      self._context = context(self._docker)

   def node_exists(self, n):
      return self._docker.dir_exists('/app/nodes/'+n.name()) 

   def set_active(self, n):
      if self.node_exists(n):
         self._context.set_active(n)
      else:
         raise dune_node_not_found(n.name())

   def get_active(self):
      return self._context.get_active()

   def create_node(self, n):
      print("Creating node ["+n.name()+"]")
      self._docker.execute_cmd(['mkdir', '-p', n.data_dir()])
      self._context.set_active(n)

   def start_node(self, n, p, is_prod):
      stdout, stderr, ec = self._docker.execute_cmd(['ls',  '/app/nodes'])

      cmd = ['sh', 'start_node.sh', n.data_dir(), n.config_dir()]
      # if node name is not found we need to create it
      if not n.name() in stdout:
         self.create_node(n)
      
      # copy config.ini to config-dir
      if n.config() == None:
         self._docker.execute_cmd(['cp', '/app/config.ini', n.config_dir()])
      else:
         self._docker.cp_from_host(n.config(), n.config_dir())

      if is_prod:
         cmd = cmd + ['-e']
         if p == None:
            cmd = cmd + ['eosio']
         else:
            cmd = cmd + [p]

      stdout, stderr, ec = self._docker.execute_cmd(cmd+[n.name()])
      print(stdout)
      print(stderr)
   
   def monitor(self, n):
      if self.dir_exists('/app/nodes/'+n.name()):
         self._docker.execute_cmd(['tail', '-f', '.'+n.name()+'.out'])
      else:
         raise dune_node_not_found(n.name())
   
   def stop_node(self, n):
      if self.dir_exists('/app/nodes/'+n.name()):
         pid = self.find_pid('/app/nodes/'+n.name())
         if pid != -1:
            print("Stopping node ["+n.name()+"]")
            self._docker.execute_cmd(['kill', pid])
         else:
            print("Node ["+n.name()+"] is not running")
      else:
         raise dune_node_not_found(n.name())
      
   def remove_node(self, n):
      self.stop_node(n)
      print("Removing node ["+n.name()+"]")
      self._docker.execute_cmd(['rm','-rf', '/app/nodes/'+n.name()])
   
   def list_nodes(self):
      print("Node Name        | Active? | Running? | HTTP           | P2P          | SHiP")
      print("----------------------------------------------------------------------------------------")
      stdout, stderr, ec = self._docker.execute_cmd(['ls', '/app/nodes'])
      ctx = self._context.get_ctx()
      for s in stdout.split():
         print(s, end='')
         if s == ctx.active:
            print('\t\t |    ✓', end='')
         else:
            print('\t\t |    ✗', end='')
         pid = self._docker.find_pid('/app/nodes/'+s)
         if pid == -1:
            print('\t   |    ✗', end='')
         else:
            print('\t   |    ✓', end='')

         print('     | '+ctx.http_port, end='')
         print(' | '+ctx.p2p_port, end='')
         print(' | '+ctx.ship_port, end='')
   
   def export_node(self, n, dir):
      if self.dir_exists('/app/nodes/'+n.name()):
         print("Exporting data from node ["+n.name()+"] to location "+dir)
         self.tar_dir(n.name(), 'nodes/'+n.name())
         self.cp_to_host('/app/'+n.name()+'.tgz', dir)
         self.rm('/app/'+n.name()+'.tgz')
      else:
         raise dune_node_not_found(n.name())
      
   def import_node(self, dir, n):
      print("Importing node data ["+n.name()+"]")
      if self.node_exists(n):
         self.stop_node(n)
         self.remove_node(n)
      self._docker.cp_from_host(dir, '/app')
      self._docker.untar('/app/'+n.name()+'.tgz')
      self._docker.rm('/app/'+n.name()+'.tgz')
   
   def get_wallet_pw(self):
      pw, stderr, ec = self._docker.execute_cmd(['cat', '.wallet.pw'])
      return pw

   def unlock_wallet(self):
      self._docker.execute_cmd(['cleos', 'wallet', 'unlock', '--password', self.get_wallet_pw()])
   
   def import_key(self, k):
      self.unlock_wallet()
      self._docker.execute_cmd(['cleos', 'wallet', 'import', '--private-key', k])
   
   def create_key(self):
      stdout, stderr, ec = self._docker.execute_cmd(['cleos', 'create', 'key', '--to-console'])
      return stdout

   def create_account(self, n, c):
      keys = self.create_key() 
      priv = keys.splitlines()[0].split(':')[1][1:]
      pub  = keys.splitlines()[1].split(':')[1][1:]
      print("Creating account ["+n+"] with key pair [Private: "+priv+", Public: "+pub+"]")
      if c == None:
         stdout, stderr, ec = self._docker.execute_cmd(['cleos', 'create', 'account', 'eosio', n, pub])
      else:
         stdout, stderr, ec = self._docker.execute_cmd(['cleos', 'create', 'account', c, n, pub])
      self.import_key(priv)
      print(ec)
      print(stderr)

