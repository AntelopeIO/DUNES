import subprocess
import os

class node:
   _name = ""
   _cfg  = ""
   def __init__(self, nm, cfg):
      self._name = nm
      self._cfg  = cfg
   
   def name(self):
      return self._name

   def config(self):
      return self._cfg
   
   def data_dir(self):
      return '/app/nodes/'+self.name()
   
   def config_dir(self):
      return '/app/nodes/'+self.name()

class dune_error(Exception):
   pass

class dune_node_not_found(dune_error):
   _name = ""
   def __init__(self, n):
      self._name = n
   
   def name(self):
      return self._name

class docker:
   _container = "dune_container"
   def __init__(self):
      # check if container is running
      proc = subprocess.Popen(['docker', 'ps'], stdout=subprocess.PIPE)
      stdout, stderr = proc.communicate()

      # if container is not in the list then create one
      if not self._container in str(stdout):
         # start a new container
         print("Creating docker container ["+self._container+"]")
         cmd_str = "docker run --name="+self._container+" dune:latest tail -f &> /dev/null &"
         os.system(cmd_str)
   
   def file_exists(self, fn):
      return self.execute_cmd(['test', '-f', fn])[2] == 0
   
   def dir_exists(self, d):
      return self.execute_cmd(['test', '-d', d])[2] == 0

   def tar_dir(self, n, d):
      return self.execute_cmd(['tar', 'cvzf', n+'.tgz', d])
 
   def untar(self, d):
      return self.execute_cmd(['tar', 'xvzf', d])
   
   def cp(self, a, b):
      proc = subprocess.Popen(['docker', 'cp', a, b], 
                              stdout=subprocess.PIPE)
      proc.communicate()

   def cp_to_host(self, cf, hf):
      self.cp(self._container+':'+cf, hf)
   
   def cp_from_host(self, hf, cf):
      self.cp(hf, self._container+":"+cf)
   
   def rm(self, f):
      self.execute_cmd(['rm', '-rf', f])


   def find_pid(self, s):
      stdout, stderr, ec = self.execute_cmd(['ps', 'ax'])
      for line in stdout.splitlines(True):
         if "PID TTY" in line:
            continue
         else:
            if s in line:
               return line.split()[0]
      
      return -1

   def destroy(self):
      print("Destroying docker container ["+self._container+"]")
      proc = subprocess.Popen(['docker', 'container', 'stop', self._container], 
                              stdout=subprocess.PIPE)
      proc.communicate()
      proc = subprocess.Popen(['docker', 'container', 'rm', self._container], 
                              stdout=subprocess.PIPE)
      proc.communicate()


   def execute_cmd(self, cmd):
      proc = subprocess.Popen(['docker', 'container', 'exec', self._container] + cmd, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      stdout, stderr = proc.communicate()
      return [stdout.decode('UTF-8'), stderr.decode('UTF-8'), proc.poll()]

   def execute_bg_cmd(self, cmd):
      return self.execute_cmd(cmd+['&'])


   def create_node(self, n):
      print("Creating node ["+n.name()+"]")
      self.execute_cmd(['mkdir', '-p', n.data_dir()])

   def start_node(self, n, p, is_prod):
      stdout, stderr, ec = self.execute_cmd(['ls',  '/app/nodes'])

      cmd = ['/app/start_node.sh', n.data_dir(), n.config_dir()]
      # if node name is not found we need to create it
      if not n.name() in stdout:
         self.create_node(n)
      if is_prod:
         print('is_prod')
         cmd = cmd + ['-e']
         if p == None:
            cmd = cmd + ['eosio']
         else:
            cmd = cmd + [p]

      self.execute_bg_cmd(cmd+[n.name()])
   
   def monitor(self, n):
      if self.dir_exists('/app/nodes/'+n.name()):
         proc = subprocess.Popen(['docker', 'container', 'exec', self._container, 'tail', '-f', '/app/nodes/'+n.name()+'.out'])
         proc.communicate()
      else:
         raise dune_node_not_found(n.name())
   
   def stop_node(self, n):
      if self.dir_exists('/app/nodes/'+n.name()):
         pid = self.find_pid('/app/nodes/'+n.name())
         if pid != -1:
            print("Stopping node ["+n.name()+"]")
            self.execute_cmd(['kill', pid])
         else:
            print("Node ["+n.name()+"] is not running")
      else:
         raise dune_node_not_found(n.name())
      
   def remove_node(self, n):
      self.stop_node(n)
      print("Removing node ["+n.name()+"]")
      self.execute_cmd(['rm','-rf', '/app/nodes/'+n.name()])
   
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
      if self.dir_exists('/app/nodes/'+n.name()):
         self.stop_node(n)
         self.remove_node(n)
      self.cp_from_host(dir, '/app')
      self.untar('/app/'+n.name()+'.tgz')
      self.rm('/app/'+n.name()+'.tgz')
      