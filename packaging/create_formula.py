#! /usr/bin/env python3

import os
import sys
import argparse
import hashlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__)+'/..')))
from src.dunes.version import version_full

def get_release_assets(repo, release):
   """Get the assets for the release."""

   url = 'https://github.com/'+repo+'/archive/refs/tags/v'+release+'.tar.gz'
   #https://github.com/AntelopeIO/DUNES/archive/refs/tags/v1.1.2.tar.gz
   os.system('wget '+url)

def create_homebrew_formula(src_dir):
   """Create the formula for the homebrew package."""

   digest = ""
   get_release_assets('antelopeio/DUNES', version_full())

   with open('v'+version_full()+'.tar.gz', 'rb') as f:
      sha256 = hashlib.sha256()
      while True:
         data = f.read(65536)
         if not data:
            break
         sha256.update(data)
      digest = sha256.hexdigest()

   formula = """class Dunes < Formula
   desc "Docker Utilities for Node Execution and Subsystems (DUNES)"
   homepage "https://www.github.com/antelopeio/DUNES"
   revision 0
   url "https://github.com/larryk85/homebrew-dunes/releases/download/v{vers}/dunes.tar.gz"
   version "{vers}"
   sha256 "{sha256}"

   depends_on "docker"
   depends_on "python3"
   depends_on "pyinstaller"

   def install
      system "pip3", "install", "argcomplete", "requests"
      system "./install.sh " "macos " "."
   end

   test do
      system "false"
   end
end
__END__
   """

   formula = formula.format(vers=version_full(), sha256=digest)

   with open('dunes.rb', 'w') as f:
      f.write(formula)

if __name__ == '__main__':
   parser = argparse.ArgumentParser(description='Create a homebrew formula for DUNES.')
   parser.add_argument('--src', dest='src', required=True, help='The path to the source directory.')
   args = parser.parse_args()

   create_homebrew_formula(args.src)