from docker import docker
from context import context

import os, platform
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
   _token_priv_key = "5JPJoZXizFVi19wHkboX5fwwEU2jZVvtSJpQkQu3uqgNu8LNdQN"
   _token_pub_key  = "EOS6v86d8DAxjfGu92CLrnEzq7pySpVWYV2LjaxPaDJJvyf9Vpx5R"

   def __init__(self):
      self._docker = docker('dune_container', 'dune:latest')
      self._wallet_pw = self.get_wallet_pw()
      self._context = context(self._docker)

   def node_exists(self, n):
      return self._docker.dir_exists('/app/nodes/'+n.name()) 

   def is_node_running(self, n):
     return self._docker.find_pid('/app/nodes/'+n.name()+' ') != -1

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

   def start_node(self, n, snapshot=None):
      stdout, stderr, ec = self._docker.execute_cmd(['ls',  '/app/nodes'])

      if self.is_node_running(n):
         print("Node ["+n.name()+"] is already running.")
         return

      cmd = ['sh', 'start_node.sh', n.data_dir(), n.config_dir()]

      if snapshot != None:
         cmd = cmd + ['--snapshot /app/nodes/'+n.name()+'/snapshots/'+snapshot+' -e']
      else:
         cmd = cmd + [' ']

      # if node name is not found we need to create it
      if not n.name() in stdout:
         self.create_node(n)
      
      # copy config.ini to config-dir
      if n.config() == None:
         self._docker.execute_cmd(['cp', '/app/config.ini', n.config_dir()])
      else:
         print("Using Configuration ["+n.config_dir()+"/config.ini]")
         self._docker.cp_from_host(n.config(), n.config_dir())

      stdout, stderr, ec = self._docker.execute_cmd(cmd+[n.name()])
      print(stdout)
      print(stderr)
   
   def cleos_cmd(self, cmd):
      self.unlock_wallet()
      return self._docker.execute_cmd(['cleos']+cmd)

   def monitor(self):
      stdout, stderr, ec = self.cleos_cmd(['get', 'info'])
      print(stdout)
      if ec != 0:
         print(stderr)
         raise dune_error
   
   def stop_node(self, n):
      if self.node_exists(n):
         if self.is_node_running(n):
            pid = self._docker.find_pid('/app/nodes/'+n.name()+' ')
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
   
   def destroy(self):
      self._docker.destroy()
   
   def stop_container(self):
      self._docker.stop()
   
   def start_container(self):
      self._docker.start()
   
   def list_nodes(self, simple=False):
      if simple:
         print("Node|Active|Running|HTTP|P2P|SHiP")
      else:
         print("Node Name        | Active? | Running? | HTTP           | P2P          | SHiP")
         print("--------------------------------------------------------------------------------------")
      stdout, stderr, ec = self._docker.execute_cmd(['ls', '/app/nodes'])
      ctx = self._context.get_ctx()
      for s in stdout.split():
         print(s, end='')
         if s == ctx.active:
            if simple:
               print('|Y', end='')
            else:
               print('\t\t |    ✓', end='')
         else:
            if simple:
               print('|N', end='')
            else:
               print('\t\t |    ✗', end='')
         if not self.is_node_running( node(s) ):
            if simple:
               print('|N', end='')
            else:
               print('\t   |    ✗', end='')
         else:
            if simple:
               print('|Y', end='')
            else:
               print('\t   |    ✓', end='')

         if simple:
            print('|'+ctx.http_port+'|'+ctx.p2p_port+'|'+ctx.ship_port)
         else:
            print('     | '+ctx.http_port+' | '+ctx.p2p_port+' | '+ctx.ship_port)
   
   def export_node(self, n, dir):
      if self.node_exists(n):
         self.set_active(n)
         print("Exporting data from node ["+n.name()+"] to location "+dir)
         if not self.is_node_running(n):
            self.start_node(n)
         self.create_snapshot()
         self.stop_node(n)
         self._docker.execute_cmd(['mkdir', '-p', '/app/tmp/'+n.name()])
         self._docker.execute_cmd(['cp', '-R', '/app/nodes/'+n.name()+'/blocks', '/app/tmp/'+n.name()+'/blocks'])
         self._docker.execute_cmd(['cp', '/app/nodes/'+n.name()+'/config.ini', '/app/tmp/'+n.name()+'/config.ini'])
         self._docker.execute_cmd(['cp', '-R', '/app/nodes/'+n.name()+'/protocol_features', '/app/tmp/'+n.name()+'/protocol_features'])
         self._docker.execute_cmd(['cp', '-R', '/app/nodes/'+n.name()+'/snapshots', '/app/tmp/'+n.name()+'/snapshots'])
         self._docker.tar_dir(n.name(), 'tmp/'+n.name())
         self._docker.cp_to_host('/app/'+n.name()+'.tgz', dir)
         self._docker.rm('/app/'+n.name()+'.tgz')
         self._docker.rm('/app/tmp/'+n.name())
         self.start_node(n)
      else:
         raise dune_node_not_found(n.name())
      
   def import_node(self, dir, n):
      print("Importing node data ["+n.name()+"]")
      if self.node_exists(n):
         self.remove_node(n)
      stdout, stderr, ec = self._docker.cp_from_host(dir, '/app/tmp.tgz')
      if ec != 0:
         print(stderr)
         raise dune_error
      self._docker.untar('/app/tmp.tgz')
      self._docker.rm('/app/tmp.tgz')
      stdout, stderr, ec = self._docker.execute_cmd(['ls', '/app/tmp'])
      self._docker.execute_cmd(['mkdir', '-p', '/app/nodes/'+n.name()])
      self._docker.execute_cmd(['mv', '/app/tmp/'+stdout.split()[0]+'/blocks/blocks.index', '/app/nodes/'+n.name()+'/blocks/blocks.index'])
      self._docker.execute_cmd(['mv', '/app/tmp/'+stdout.split()[0]+'/blocks/blocks.log', '/app/nodes/'+n.name()+'/blocks/blocks.log'])
      self._docker.execute_cmd(['mv', '/app/tmp/'+stdout.split()[0]+'/config.ini', '/app/nodes/'+n.name()+'/config.ini'])
      self._docker.execute_cmd(['mv', '/app/tmp/'+stdout.split()[0]+'/protocol_features', '/app/nodes/'+n.name()+'/protocol_features'])
      self._docker.execute_cmd(['mv', '/app/tmp/'+stdout.split()[0]+'/snapshots', '/app/nodes/'+n.name()+'/snapshots'])
      self._docker.rm('/app/tmp/'+stdout.split()[0])
      stdout, stderr, ec = self._docker.execute_cmd(['ls', '/app/nodes/'+n.name()+'/snapshots'])
      self.start_node(n, stdout.split()[0])
      self.set_active(n)
   
   def get_wallet_pw(self):
      pw, stderr, ec = self._docker.execute_cmd(['cat', '.wallet.pw'])
      return pw

   def unlock_wallet(self):
      self._docker.execute_cmd(['cleos', 'wallet', 'unlock', '--password', self.get_wallet_pw()])
   
   def import_key(self, k):
      self.cleos_cmd(['wallet', 'import', '--private-key', k])
   
   def create_key(self):
      stdout, stderr, ec = self.cleos_cmd(['create', 'key', '--to-console'])
      return stdout

   def create_account(self, n, c):
      keys = self.create_key() 
      priv = keys.splitlines()[0].split(':')[1][1:]
      pub  = keys.splitlines()[1].split(':')[1][1:]
      print("Creating account ["+n+"] with key pair [Private: "+priv+", Public: "+pub+"]")
      if c == None:
         stdout, stderr, ec = self.cleos_cmd(['create', 'account', 'eosio', n, pub])
      else:
         stdout, stderr, ec = self.cleos_cmd(['create', 'account', c, n, pub])
      self.import_key(priv)
      print(ec)
      print(stderr)
   
   def execute_cmd(self, args):
      self._docker.execute_cmd2(args)
   
   def build_cmake_proj(self, dir, flags):
      container_dir = self._docker.abs_host_path(dir)
      build_dir = container_dir+'/build'
      if not self._docker.dir_exists(build_dir):
         self._docker.execute_cmd(['mkdir', '-p', build_dir])
      self._docker.execute_cmd2(['cmake', '-S', container_dir, '-B', build_dir]+flags)
      self._docker.execute_cmd2(['cmake', '--build', build_dir])
   
   def create_snapshot(self):
      ctx = self._context.get_ctx()
      url = "http://"+ctx.http_port+"/v1/producer/create_snapshot"
      stdout, stderr, ec = self._docker.execute_cmd(['curl', '-X', 'POST', url])
      print(stdout)
      print(stderr)
      print(url)
   
   def deploy_contract(self, dir, acnt):
      stdout, stderr, ec = self.cleos_cmd(['set', 'contract', acnt, dir])

      if ec != 0:
         print(stderr)
         raise dune_error()
      else:
         print(stdout)
   
   def bootstrap_system(self):
      self.deploy_contract('/app/mandel-contracts/build/contracts/eosio.system', 'eosio')
      self.create_account('eosio.token', 'eosio')
      self.deploy_contract('', acnt)