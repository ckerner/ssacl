#!/usr/bin/env python
"""

This is used to backup the ACLs on the files in the cluster.        

Chad Kerner, Senior Storage Engineer
Storage Enabling Technologies
National Center for Supercomputing Applications
ckerner@illinois.edu    chad.kerner@gmail.com

There is _NO_ support. Use it at your own risk.

If you find a bug, fix it.  Then, send me the diff and I'll merge it into the code.

"""

from __future__ import print_function
import ldap
import sys
import os
import pprint
from tempfile import mkstemp
import json
from ssacl import *

acl_directory = '/mforge/admin/acl/'

def parse_options( argv ):
    """
    This function handles the parsing of the command line arguments.

    Args:
      argv: A list of command line arguments, passed in from sys.argv

    Returns
      options: A dictionary of the command line option settings
      args   : A list of files

    """

    import argparse
    import textwrap
    parser = argparse.ArgumentParser(
                                     formatter_class = argparse.RawTextHelpFormatter,
                                     prog = 'backup_acls.py',
                                     description = textwrap.dedent('''\
                                             backup_acls.py - Backup the ACLs on the files in the cluster
                              
                                             '''),
                                     epilog = textwrap.dedent('''\

                                             This utility requires IBM SpectrumScale to be installed in the default location.

                                             Chad Kerner - ckerner@illinois.edu
                                             Senior Storage Engineer, Storage Enabling Technologies
                                             National Center for Supercomputing Applications
                                             University of Illinois, Urbana-Champaign''')
                                    )

    parser.add_argument( "-f", "--filename",
                         dest = "filename",
                         default = None,
                         action = 'store',
                         help = "The file sysystem path to map to the specified group. Default: %(default)s")

    parser.add_argument( "-v", "--verbose",
                         dest = "verbose",
                         default = False,
                         action = 'store_true',
                         help = "Run in verbose mode. Default: %(default)s")

    parser.add_argument( "-d", "--debug",
                         dest = "debug",
                         default = False,
                         action = 'store_true',
                         help = "Run in debug mode. Default: %(default)s")

    options, args = parser.parse_known_args( argv )
    return ( options, args )


if __name__ == '__main__':
   ( options, args ) = parse_options( sys.argv[1:] )

   if options.filename == None:
      print("You must specify a file to parse.")
      sys.exit(1)

   pfile = open( options.filename, 'r' )
   for line in pfile:
       idx = line.find(' -- ') + 4
       #idx = idx + 4 + 4
       fqpn = line[idx:].rstrip()
       #if options.verbose:
       #   print("Processing: %s" % (fqpn))


       myacl = mmacls( fqpn )
       acl = json.dumps( myacl.acls )
       if options.verbose:
          print("   ACL: %s" % ( acl ))

       if line.split()[5].startswith('d'):
          myacl.get_default_acl()
          dacl = json.dumps( myacl.default_acls )
          if options.verbose:
             print("  DACL: %s" % ( dacl ) )

   pfile.close()

