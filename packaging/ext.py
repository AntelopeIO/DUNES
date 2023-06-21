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
import zipfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__)+'/..')))
from src.dunes.version import version_full

def create_executable(specpath, name, src, work_path):
   """Create the 'dunes' executable via pyinstaller."""
      
   # Create the executable.
   pyinstaller_command = ['python', '-m', 'PyInstaller', '--onefile', '--name='+name, src, '--specpath', specpath, '--noconfirm', '--workpath', work_path]
   
   if not subprocess.run(pyinstaller_command, stderr=None, check=False).returncode:
      return True
   
   print('Failed to create executable.', file=sys.stderr)
   return False

def create_archive_or_install(directory, archive_file, layout):
   """Create a tarball of the 'dunes' executable."""

   subprefix = ''
   install = False

   if layout == 'macos':
      install = True
      prefix = '/opt/homebrew/Cellar/dunes/'+version_full()
      subprefix = prefix+'/opt/dunes'
   elif layout == 'linux':
      prefix = '/usr'
      subprefix = prefix+'/opt/dunes'
   elif layout == 'win':
      prefix = '/'
      subprefix = prefix+'/dunes'

   with tempfile.TemporaryDirectory() as temp_dir:
      if install:
         path = prefix
      else:
         path = temp_dir + '/' + prefix

      os.makedirs(path, exist_ok=True)
      os.makedirs(path+'/bin', exist_ok=True)
      os.makedirs(path+'/'+subprefix, exist_ok=True)
      os.makedirs(path+'/'+subprefix+'/licenses', exist_ok=True)


      exe_name = 'dunes.exe' if layout == 'win' else 'dunes'

      shutil.copy(directory+'/dist/'+exe_name, path+'/bin/'+exe_name)
      shutil.copyfile(directory+'/LICENSE', path+'/'+subprefix+'/licenses/LICENSE')
      shutil.copytree(directory+'/plugin_example', path+'/'+subprefix+'/plugin_example', dirs_exist_ok=True)
      shutil.copytree(directory+'/docs', path+'/'+subprefix+'/docs', dirs_exist_ok=True)

      if not install:
         if layout == 'macos' or layout == 'linux':
            with tarfile.open(archive_file, 'w:gz') as tf:
               for file in glob.glob(path+'/**/*', recursive=True):
                  print(file)
                  tf.add(file, arcname=file[len(temp_dir)+1:]) 

         elif layout == 'win':
            with zipfile.ZipFile(archive_file, 'w', zipfile.ZIP_DEFLATED) as zf:
               for file in glob.glob(temp_dir+'/**/*', recursive=True):
                  print(file)
                  zf.write(file, arcname=file[len(temp_dir)+1:])
      
if __name__ == '__main__':
   # Parse command line arguments.
   parser = argparse.ArgumentParser(description='Package the DUNES executable.')
   parser.add_argument('--specpath', default='.', help='Path to the spec file.')
   parser.add_argument('--src', default='.', help='Path to the source directory.')
   parser.add_argument('--archive', default='dunes', help='Name of the archive.')
   parser.add_argument('--layout', default='', help='Name of the layout used, macos, linux, win., defaults to which plaform is used to run the script.')
   args = parser.parse_args()

   temp_d = tempfile.TemporaryDirectory()

   with tempfile.TemporaryDirectory() as temp_d:
      # Create the executable.
      if not create_executable(args.specpath, 'dunes', args.src+'/src/dunes/__main__.py', temp_d):
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

      archive_name = args.archive+'.tar.gz'
      if args.layout == 'win':
         archive_name = args.archive+'.zip'
         create_executable(args.specpath, 'installer.exe', args.src+'/packaging/windows_installer.py', temp_d)

      create_archive_or_install(args.src, archive_name, args.layout)

