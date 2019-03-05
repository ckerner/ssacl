#!/usr/bin/env python
#=====================================================================================
# Chad Kerner, Senior Systems Engineer
# Storage Enabling Technologies
# National Center for Supercomputing Applications
# ckerner@illinois.edu     chad.kerner@gmail.com
#=====================================================================================
#
# This was born out of a need to programmatically interface with IBM Spectrum
# Scale or the software formerly knows as GPFS.
#
# There is NO support, use it at your own risk.  Although I have not coded
# anything too awfully dramatic in here.
#
# If you find a bug, fix it.  Then send me the diff and I will merge it into
# the code.
#
# You may want to pull often because this is being updated quite frequently as
# our needs arise in our clusters.
#
#=====================================================================================

from __future__ import print_function
from subprocess import Popen, PIPE
import sys
import os
import shlex
from stat import *
from tempfile import mkstemp

#get_default_owner_name
#get_default_group_name
#get_default_acl
#get_mask
#set_mask
#get_file_acl
#get_group_acl
#set_group_acl
#check_group_acl

def run_cmd( cmdstr=None ):
    """
    Wrapper around subprocess module calls.
    """
    if not cmdstr:
       return None
    cmd = shlex.split(cmdstr)
    subp = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (outdata, errdata) = subp.communicate()
    if subp.returncode != 0:
       msg = "Error\n Command: {0}\n Message: {1}".format(cmdstr,errdata)
       raise UserWarning( msg )
       exit( subp.returncode )
    return( outdata )


def get_acl( fnam ):
    fqpn = os.path.abspath( fnam )
    stats = os.stat( fqpn )
    mode = stats[ST_MODE]
    cmd = '/usr/lpp/mmfs/bin/mmgetacl '
    if S_ISDIR( mode ):
       print("Directory: %s" % ( fqpn ) )
       cmd = cmd + '-d ' + fqpn
    elif S_ISREG( mode ):
       print("File: %s" % ( fqpn ) )
       cmd = cmd + fqpn
    else:
       print("Unknown error")
       sys.exit(1)

    output = run_cmd( cmd )
    for line in output:
        if '#owner:' in line:
           owner = line.split(':')[1]
           print("Owner: %s" % ( owner ))
        print(line,end="")

if __name__ == '__main__':
   get_acl( '/data/acl/a' )

