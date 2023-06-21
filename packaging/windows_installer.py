#! /usr/bin/env python3

import os
import sys
import tempfile
import ctypes
import argparse
import zipfile
import wget

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__)+'/..')))
from src.dunes.version import version_full

if __name__ == "__main__":
   url = 'https://download.docker.com/win/static/stable/x86_64/docker-24.0.2.zip' 

   parser = argparse.ArgumentParser(description='Install DUNES and dependencies.')
   parser.add_argument('--install-dir', default='~/dunes', help='Path to the install to.')
   args = parser.parse_args()

   def is_admin():
      try:
         return ctypes.windll.shell32.IsUserAnAdmin()
      except:
         return False
   
   #if is_admin():
   with tempfile.TemporaryDirectory() as temp_dir:
      print('Installing Docker Engine...\n')
      fn = wget.download(url, out=temp_dir)
      with zipfile.ZipFile(fn, 'r') as zip_ref:
         zip_ref.extractall(args.install_dir)

      print('\nInstalling DUNES...\n')
      url = 'https://github.com/larryk85/test-dunes/releases/download/'+version_full()+'/dunes.zip'
      fn = wget.download(url, out=temp_dir)
      with zipfile.ZipFile(fn, 'r') as zip_ref:
         zip_ref.extractall(args.install_dir)
      
      print('\nInstallation complete...\n')
      dockerd_path = args.install_dir+'/docker/dockerd.exe'
      ctypes.windll.shell32.ShellExecuteW(None, "open", dockerd_path, "--register-service", None, 1)

      input('Press enter to exit...')
   #else:
   #   ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv[1:]), None, 1)