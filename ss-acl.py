#!/usr/bin/env python
"""
We needed to be able to modify SpectrumScale ACLs easily and in parallel, and
the interface provided by IBM, namely mmgetacl and mmputacl are less that
friendly when it comes to parsing millions of files and maintaining ACLs on
them.

The source for this is publicly available at:
          github: https://github.com/ckerner/ss-acl.git

Chad Kerner, Senior Storage Engineer
Storage Enabling Technologies
National Center for Supercomputing Applications
ckerner@illinois.edu     chad.kerner@gmail.com

This was born out of a need to programmatically interface with IBM Spectrum
Scale or the software formerly knows as GPFS.

There is NO support, use it at your own risk.  Although I have not coded
anything too awfully dramatic in here.

If you find a bug, fix it.  Then send me the diff and I will merge it into
the code.

You may want to pull often because this is being updated quite frequently as
our needs arise in our clusters.

"""

from __future__ import print_function
from subprocess import Popen, PIPE
import sys
import os
import shlex
from stat import *
from tempfile import mkstemp
import pprint

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

    :param: A string containing the command to run.
    :return: The text output of the command.
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

def get_group_acl( fnam=None, group=None ):
    """
    This function will return the group ACL of the specified file.

    :param: A string containing the filename.
    :param: A string containing the name of the group to check for.
    :return: A 4 character string:
               ???? - If the file does not exist.
               ---- - If the group does not have an ACL on the file.
                    - The actual 4 character permission mask(Ex: rw--)
    """

    myacl = get_acl( fnam )
    if myacl == None:
       return '????'
    else:
       if group in myacl['GROUPS'].keys():
          return myacl['GROUPS'][group]['PERMS']
       else:
          return '----'

def get_default_parent_acl( fnam=None ):
    """
    Fetch the default ACL of the parent directory for the specified path.  If
    a file is specified, the default ACL of the containing directory is returned.
    If a directory is specified, the default ACL for the parent of that
    directory is returned.
    """
    if not fnam:
       return None

    try:
       fqpn = os.path.dirname( os.path.abspath( fnam ) )
    except:
       return None
    return get_default_acl( fqpn )

def get_default_acl( fnam=None ):
    """
    Fetch the default ACL that is being applied.  If a file is specified, the
    default ACL of the containing directory is returned.  If a directory is
    specified, the default ACL for that directory is returned.

    :param fnam: The name of the file or directory to get the ACLs on.
    :return: Returns a dict with the following information:
             acl[FQPN] - Fully qualified pathname of the file.
             acl[TYPE] - f for file and D for directories
             acl[OWNER] - Owner of the file
             acl[GROUP] - Group of the file
             acl[USERP] - User permissions
             acl[GROUPP] - Group permissions
             acl[OTHERP] - Other permissions
             acl[MASK] - File mask
             acl[USERS]
                   [USER]
                       [PERMS]
                       [EFFECTIVE]
             acl[GROUPS]
                   [GROUP]
                       [PERMS]
                       [EFFECTIVE]
    """
    if not fnam:
       return None

    mydict = {}
    mydict['GROUPS'] = {}
    mydict['USERS'] = {}

    try:
       fqpn = os.path.abspath( fnam )
       stats = os.stat( fqpn )
    except:
       return None

    cmd = '/usr/lpp/mmfs/bin/mmgetacl -d ' + fqpn
    output = run_cmd( cmd )

    for line in output.splitlines():
        if '#owner:' in line:
           mydict['OWNER'] = line.split(':')[1]
        elif '#group:' in line:
           mydict['GROUP'] = line.split(':')[1]
        elif 'user::' in line:
           if line.split(':')[1] == '':
              mydict['USERP'] = line.split(':')[2]
           else:
              user_name=line.split(':')[1]
              mydict['USERS'][user_name] = {}
              mydict['USERS'][user_name]['PERMS']=line.split(':')[2][0:4]
              mydict['USERS'][user_name]['EFFECTIVE']=line.split(':')[3][1:5]
        elif 'group:' in line:
           if line.split(':')[1] == '':
              mydict['GROUPP'] = line.split(':')[2]
           else:
              group_name=line.split(':')[1]
              mydict['GROUPS'][group_name] = {}
              mydict['GROUPS'][group_name]['PERMS']=line.split(':')[2][0:4]
              mydict['GROUPS'][group_name]['EFFECTIVE']=line.split(':')[3][1:5]
        elif 'other::' in line:
           mydict['OTHERP'] = line.split(':')[2]
        elif 'mask::' in line:
           mydict['MASK'] = line.split(':')[2]
    return mydict

def get_acl( fnam=None ):
    """
    Fetch the file ACLs and return them in a dict.

    :param fnam: The name of the file or directory to get the ACLs on.
    :return: Returns a dict with the following information:
             acl[FQPN] - Fully qualified pathname of the file.
             acl[TYPE] - f for file and D for directories
             acl[OWNER] - Owner of the file
             acl[GROUP] - Group of the file
             acl[USERP] - User permissions
             acl[GROUPP] - Group permissions
             acl[OTHERP] - Other permissions
             acl[MASK] - File mask
             acl[USERS]
                   [USER]
                       [PERMS]
                       [EFFECTIVE]
             acl[GROUPS]
                   [GROUP]
                       [PERMS]
                       [EFFECTIVE]
    """
    if not fnam:
       return None

    mydict = {}
    mydict['GROUPS'] = {}
    mydict['USERS'] = {}

    try:
       fqpn = os.path.abspath( fnam )
       stats = os.stat( fqpn )
    except:
       return None

    mydict['FQPN'] = fqpn
    mode = stats[ST_MODE]
    if S_ISDIR( mode ):
       mydict['TYPE'] = 'd'
    elif S_ISREG( mode ):
       mydict['TYPE'] = 'f'
    else:
       mydict['TYPE'] = 'u'

    cmd = '/usr/lpp/mmfs/bin/mmgetacl ' + fqpn
    output = run_cmd( cmd )

    for line in output.splitlines():
        if '#owner:' in line:
           mydict['OWNER'] = line.split(':')[1]
        elif '#group:' in line:
           mydict['GROUP'] = line.split(':')[1]
        elif 'user::' in line:
           if line.split(':')[1] == '':
              mydict['USERP'] = line.split(':')[2]
           else:
              user_name=line.split(':')[1]
              mydict['USERS'][user_name] = {}
              mydict['USERS'][user_name]['PERMS']=line.split(':')[2][0:4]
              mydict['USERS'][user_name]['EFFECTIVE']=line.split(':')[3][1:5]
        elif 'group:' in line:
           if line.split(':')[1] == '':
              mydict['GROUPP'] = line.split(':')[2]
           else:
              group_name=line.split(':')[1]
              mydict['GROUPS'][group_name] = {}
              mydict['GROUPS'][group_name]['PERMS']=line.split(':')[2][0:4]
              mydict['GROUPS'][group_name]['EFFECTIVE']=line.split(':')[3][1:5]
        elif 'other::' in line:
           mydict['OTHERP'] = line.split(':')[2]
        elif 'mask::' in line:
           mydict['MASK'] = line.split(':')[2]
    return mydict

if __name__ == '__main__':
   # print("Get File ACL")
   # acla = get_acl( '/data/acl/a' )
   # pprint.pprint( acla )

   # print("See if group ckerner is on file /data/acl/a")
   # p = get_group_acl( '/data/acl/a', 'ckerner' )
   # print("Group perms for ckerner: %s" % ( p ))

   # print("See if group bob is on file /data/acl/a")
   # p = get_group_acl( '/data/acl/a', 'bob' )
   # print("Group perms for bob: %s" % ( p ))

   # print("See if group ckerner is on a non-existing file /data/acl/nofile")
   # p = get_group_acl( '/data/acl/nofile', 'ckerner' )
   # print("Group perms for nofile: %s" % ( p ))

   parent = get_default_acl( '/data/acl/dir_with_default' )
   pprint.pprint( parent )

   parent = get_default_parent_acl( '/data/acl/new/' )
   pprint.pprint( parent )
