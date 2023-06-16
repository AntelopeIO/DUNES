#! /usr/bin/env python3

import os
import sys
import platform
import subprocess
import argparse
import tempfile
import shutil
import tarfile
import glob
import hashlib
from src.dunes.version import version_full

def create_executable(specpath, src, work_path):
   """Create the 'dunes' executable via pyinstaller."""
      
   # Create the executable.
   pyinstaller_command = ['pyinstaller', '--onefile', '--name=dunes', src+'/src/dunes/__main__.py', '--specpath', specpath, '--noconfirm', '--workpath', work_path]
   
   if not subprocess.run(pyinstaller_command, stderr=None, check=False).returncode:
      return True
   
   print('Failed to create executable.', file=sys.stderr)
   return False

def create_tarball_or_install(directory, tar_file, layout):
   """Create a tarball of the 'dunes' executable."""

   subprefix = ''
   install = False;

   if layout == 'macos':
      install = True
      prefix = '/opt/homebrew/Cellar/dunes/'+version_full()
      subprefix = prefix+'/opt/dunes'

   with tempfile.TemporaryDirectory() as temp_dir:
      if install:
         path = prefix
      else:
         path = temp_dir + '/' + prefix

      os.makedirs(path, exist_ok=True)
      os.makedirs(path+'/bin', exist_ok=True)
      os.makedirs(path+'/'+subprefix, exist_ok=True)
      os.makedirs(path+'/'+subprefix+'/licenses', exist_ok=True)


      shutil.copy(directory+'/dist/dunes', path+'/bin/dunes')
      shutil.copyfile(directory+'/LICENSE', path+'/'+subprefix+'/licenses/LICENSE')
      shutil.copytree(directory+'/plugin_example', path+'/'+subprefix+'/plugin_example', dirs_exist_ok=True)
      shutil.copytree(directory+'/docs', path+'/'+subprefix+'/docs', dirs_exist_ok=True)

      if not install:
         with tarfile.open(tar_file, 'w:gz') as tf:
            for file in glob.glob(temp_dir+'/**/*', recursive=True):
               print(file)
               tf.add(file, arcname=file[len(temp_dir)+1:]) 
   
if __name__ == '__main__':
   # Parse command line arguments.
   parser = argparse.ArgumentParser(description='Package the DUNES executable.')
   parser.add_argument('--specpath', default='.', help='Path to the spec file.')
   parser.add_argument('--src', default='.', help='Path to the source directory.')
   parser.add_argument('--tarball', default='dunes.tar.gz', help='Name of the tarball.')
   parser.add_argument('--layout', default='', help='Name of the layout used, macos, linux, win., defaults to which plaform is used to run the script.')
   args = parser.parse_args()

   temp_dir = tempfile.TemporaryDirectory()

   # Create the executable.
   if not create_executable(args.specpath, args.src, temp_dir.name):
      sys.exit(1)
   
   if args.layout == '':
      if platform.system() == 'Darwin':
         args.layout = 'macos'
      elif platform.system() == 'Linux':
         args.layout = 'linux'
      elif platform.system() == 'Windows':
         args.layout = 'win'
      else:
         print('Unsupported platform.', file=sys.stderr)
         sys.exit(1)

   # Create the tarball.
   create_tarball_or_install(args.src, args.tarball, args.layout)

   #if args.layout == 'macos':
      #create_homebrew_formula(args.tarball)
