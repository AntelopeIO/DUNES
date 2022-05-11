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
         self._docker.execute_cmd(['cp', n.config(), n.config_dir()])
         print("Using Configuration ["+n.config()+"]")

      stdout, stderr, ec = self._docker.execute_cmd(cmd+[n.name()])
      
      if ec == 0:
         self.set_active(n)
         print("Active ["+n.name()+"]")

      print(stdout)
      print(stderr)
   
   def cleos_cmd(self, cmd):
      self.unlock_wallet()
      ctx = self._context.get_ctx()
      return self._docker.execute_cmd(['cleos', '-u', 'http://'+ctx.http_port]+cmd)

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

      if ec == 0:
         print(stdout)
      else:
         print(stderr)
         raise dune_error()
   
   def preactivate_feature(self):
      ctx = self._context.get_ctx()
      stdout, stderr, ec = self._docker.execute_cmd(['curl', '--noproxy', '-x', 'POST', ctx.http_port+'/v1/producer/schedule_protocol_feature_activations', '-d', '{"protocol_features_to_activate": ["0ec7e080177b2c02b278d5088611686b49d739925a92d9bfcacd7fc6b74053bd"]}'])

      if ec != 0:
         print(stderr)
         raise dune_error()
      else:
         print("Preactivate Features: "+stdout)
   
   def send_action(self, action, acnt, data, permission='eosio@active'):
      stdout, stderr, ec = self.cleos_cmd(['push', 'action', acnt, action, data, '-p', permission])
      if ec == 0:
         print(stdout)
      else:
         print(stderr)
   
   def features(self):
      return ["KV_DATABASE",
              "ACTION_RETURN_VALUE",
              "BLOCKCHAIN_PARAMETERS",
              "GET_SENDER",
              "FORWARD_SETCODE",
              "ONLY_BILL_FIRST_AUTHORIZER",
              "RESTRICT_ACTION_TO_SELF",
              "DISALLOW_EMPTY_PRODUCER_SCHEDULE",
              "FIX_LINKAUTH_RESTRICTION",
              "REPLACE_DEFERRED",
              "NO_DUPLICATE_DEFERRED_ID",
              "ONLY_LINK_TO_EXISTING_PERMISSION",
              "RAM_RESTRICTIONS",
              "WEBAUTHN_KEY",
              "WTMSIG_BLOCK_SIGNATURES"]

   def activate_feature(self, code_name):
      if code_name == "KV_DATABASE":
         self.send_action('activate', 'eosio', '["825ee6288fb1373eab1b5187ec2f04f6eacb39cb3a97f356a07c91622dd61d16"]', 'eosio@active')
      elif code_name == "ACTION_RETURN_VALUE":
         self.send_action('activate', 'eosio', '["c3a6138c5061cf291310887c0b5c71fcaffeab90d5deb50d3b9e687cead45071"]', 'eosio@active')
      elif code_name == "BLOCKCHAIN_PARAMETERS":
         self.send_action('activate', 'eosio', '["5443fcf88330c586bc0e5f3dee10e7f63c76c00249c87fe4fbf7f38c082006b4"]', 'eosio@active')
      elif code_name == "GET_SENDER":
         self.send_action('activate', 'eosio', '["f0af56d2c5a48d60a4a5b5c903edfb7db3a736a94ed589d0b797df33ff9d3e1d"]', 'eosio@active')
      elif code_name == "FORWARD_SETCODE":
         self.send_action('activate', 'eosio', '["2652f5f96006294109b3dd0bbde63693f55324af452b799ee137a81a905eed25"]', 'eosio@active')
      elif code_name == "ONLY_BILL_FIRST_AUTHORIZER":
         self.send_action('activate', 'eosio', '["8ba52fe7a3956c5cd3a656a3174b931d3bb2abb45578befc59f283ecd816a405"', 'eosio@active')
      elif code_name == "RESTRICT_ACTION_TO_SELF":
         self.send_action('activate', 'eosio', '["ad9e3d8f650687709fd68f4b90b41f7d825a365b02c23a636cef88ac2ac00c43"]', 'eosio@active')
      elif code_name == "DISALLOW_EMPTY_PRODUCER_SCHEDULE":
         self.send_action('activate', 'eosio', '["68dcaa34c0517d19666e6b33add67351d8c5f69e999ca1e37931bc410a297428"]', 'eosio@active')
      elif code_name == "FIX_LINKAUTH_RESTRICTION":
         self.send_action('activate', 'eosio', '["e0fb64b1085cc5538970158d05a009c24e276fb94e1a0bf6a528b48fbc4ff526"]', 'eosio@active')
      elif code_name == "REPLACE_DEFERRED":
         self.send_action('activate', 'eosio', '["ef43112c6543b88db2283a2e077278c315ae2c84719a8b25f25cc88565fbea99"]', 'eosio@active')
      elif code_name == "NO_DUPLICATE_DEFERRED_ID":
         self.send_action('activate', 'eosio', '["4a90c00d55454dc5b059055ca213579c6ea856967712a56017487886a4d4cc0f"]', 'eosio@active')
      elif code_name == "ONLY_LINK_TO_EXISTING_PERMISSION":
         self.send_action('activate', 'eosio', '["1a99a59d87e06e09ec5b028a9cbb7749b4a5ad8819004365d02dc4379a8b7241"]', 'eosio@active')
      elif code_name == "RAM_RESTRICTIONS":
         self.send_action('activate', 'eosio', '["4e7bf348da00a945489b2a681749eb56f5de00b900014e137ddae39f48f69d67"]', 'eosio@active')
      elif code_name == "WEBAUTHN_KEY":
         self.send_action('activate', 'eosio', '["4fca8bd82bbd181e714e283f83e1b45d95ca5af40fb89ad3977b653c448f78c2"]', 'eosio@active')
      elif code_name == "WTMSIG_BLOCK_SIGNATURES":
         self.send_action('activate', 'eosio', '["299dcb6af692324b899b39f16d5a530a33062804e41f09dc97e9f156b4476707"]', 'eosio@active')
      else:
         print("Feature Not Found")
         raise dune_error()
   
   def bootstrap_system(self, full):
      self.preactivate_feature()
      if full:
         # create system accounts
         self.create_account('eosio.token', 'eosio')
         self.create_account('eosio.bpay', 'eosio')
         self.create_account('eosio.msig', 'eosio')
         self.create_account('eosio.names', 'eosio')
         self.create_account('eosio.ram', 'eosio')
         self.create_account('eosio.ramfee', 'eosio')
         self.create_account('eosio.saving', 'eosio')
         self.create_account('eosio.stake', 'eosio')
         self.create_account('eosio.vpay', 'eosio')
         self.create_account('eosio.rex', 'eosio')

      # activate features
      self.deploy_contract('/app/mandel-contracts/build/contracts/eosio.boot', 'eosio')

      for f in self.features():
         self.activate_feature(f)

      if full:
         self.deploy_contract('/app/mandel-contracts/build/contracts/eosio.system', 'eosio')
         self.deploy_contract('/app/mandel-contracts/build/contracts/eosio.token', 'eosio.token')
         self.deploy_contract('/app/mandel-contracts/build/contracts/eosio.msig', 'eosio.msig')
      