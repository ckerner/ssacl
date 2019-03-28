#!/usr/bin/env python
"""
We needed to be able to modify SpectrumScale ACLs easily and in parallel, and
the interface provided by IBM, namely mmgetacl and mmputacl are less that
friendly when it comes to parsing millions of files and maintaining ACLs on
them.

The source for this is publicly available at:
          github: https://github.com/ckerner/ssacl.git

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

DRYRUN = 0
MMGETACL = '/usr/lpp/mmfs/bin/mmgetacl '
MMPUTACL = '/usr/lpp/mmfs/bin/mmputacl '

class mmacls:
      """
      This class will handle the manipulation of the SpectrumScale ACLs
      on the files that need them.
      """
      def __init__( self, fname=None ):
          self.debug = False
          self.dryrun = False
          self.verbose = False
          self.fname = fname
          try:
             self.filename = os.path.abspath( fname )
             self.stats = os.stat( self.filename )
          except:
             self.filename = None
             return None
          if S_ISDIR(self.stats[ST_MODE]):
             self.dirname = self.filename
          else:
             self.dirname = os.path.dirname( self.filename )
          self.get_acl()
          #self.get_default_acl()

      def dump_mmacl( self ):
          print( "File: " + self.filename )
          print( "Directory: " + self.dirname )
          print( "ACL: " )
          print( self.acls )
          print( "Default ACL: " )
          #print( self.default_acls )

      def dump_raw_acl( self ):
          cmd = MMGETACL + self.filename
          output = run_cmd( cmd )
          for line in output.splitlines():
              print( line )
          print("")

      def clear_acls( self ):
          if 'MASK' in self.acls:
             del self.acls['MASK']
          if 'USERS' in self.acls:
             del self.acls['USERS']
          if 'GROUPS' in self.acls:
             del self.acls['GROUPS']

      def get_acl( self ):
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

          mydict = {}
          mydict['GROUPS'] = {}
          mydict['USERS'] = {}
          mydict['FQPN'] = self.filename

          cmd = MMGETACL + self.filename
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
          self.acls = mydict

      def get_default_acl( self ):
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

          mydict = {}
          mydict['GROUPS'] = {}
          mydict['USERS'] = {}
          mydict['FQPN'] = self.dirname

          cmd = MMGETACL + '-d ' + self.dirname
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
          self.default_acls = mydict

      def get_group_acl( self, group=None ):
          """
          This function will return the group ACL of the specified file.

          :param: A string containing the filename.
          :param: A string containing the name of the group to check for.
          :return: A 4 character string:
                     ???? - If the file does not exist.
                     ---- - If the group does not have an ACL on the file.
                          - The actual 4 character permission mask(Ex: rw--)
          """

          if self.acls == None:
             return '????'
          else:
             if group in self.acls['GROUPS'].keys():
                return self.acls['GROUPS'][group]['PERMS']
             else:
                return '----'


      def set_default_acl( self, aclfile=None ):
          cmd = MMPUTACL + '-d -i ' + aclfile + ' ' + self.filename
          if self.dryrun:
             print( cmd )
          else:
             if self.verbose:
                print( cmd )
             run_cmd( cmd )

      def set_acl( self, aclfile=None ):
          cmd = MMPUTACL + '-i ' + aclfile + ' ' + self.filename
          if self.dryrun:
             print( cmd )
          else:
             if self.verbose:
                print( cmd )
             run_cmd( cmd )

      def debug_on( self ):
          """
          Turn debug on.      
          """
          self.debug = True

      def debug_off( self ):
          """
          Turn debug off.      
          """
          self.debug = False

      def toggle_debug( self ):
          """
          Toggle debug mode.
          """
          if self.debug == True:
             self.debug = False
          else:
             self.debug = True

      def dryrun_on( self ):
          """
          Turn dryrun on.      
          """
          self.dryrun = True

      def dryrun_off( self ):
          """
          Turn dryrun off.      
          """
          self.dryrun = False

      def toggle_dryrun( self ):
          """
          Toggle dryrun mode.
          """
          if self.dryrun == False:
             self.dryrun = True
          else:
             self.dryrun = False

      def verbose_on( self ):
          """
          Turn verbose on.      
          """
          self.verbose = True

      def verbose_off( self ):
          """
          Turn verbose off.      
          """
          self.verbose = False

      def toggle_verbose( self ):
          """
          Toggle verbose mode.
          """
          if self.verbose == False:
             self.verbose = True
          else:
             self.verbose = False


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
    if subp.returncode == 22:
       return( 'File is not in gpfs.' )
    if subp.returncode != 0:
       msg = "Error\n Command: {0}\n Message: {1}".format(cmdstr,errdata)
       raise UserWarning( msg )
       exit( subp.returncode )
    return( outdata )

def chown_file( fnam=None, owner=-1, group=-1 ):
    """
    To leave the owner or group the same, set it to -1
    """
    try:
       os.chown( fnam, owner, group )
    except:
       print("Error: %s %s %s" % ( fnam, owner, group ) )

def write_acl_file( aclfile=None, myacls=None ):
    """
    Write an ACL file. This does not have to be part of a class. You may
    want to write one for other thigns.
    """
    if not myacls:
       return None

    if not aclfile:
       return None

    fd = open( aclfile, "w" )
    fd.write( "user::" + myacls['USERP'] + "\n" )
    fd.write( "group::" + myacls['GROUPP'] + "\n" )
    fd.write( "other::" + myacls['OTHERP'] + "\n" )
    if 'MASK' in myacls.keys():
       fd.write( "mask::" + myacls['MASK'] + "\n" )
    else:
       # If we have USER and GROUP ACLs, we need a default mask
       if 'USERS' in myacls.keys():
          if 'GROUPS' in myacls.keys():
             fd.write( "mask::rwxc" + "\n" )

    if 'USERS' in myacls.keys():
       for user in myacls['USERS'].keys():
           fd.write( "user:" + user + ":" + myacls['USERS'][user]['PERMS'] + "\n" )

    if 'GROUPS' in myacls.keys():
       for group in myacls['GROUPS'].keys():
           fd.write( "group:" + group + ":" + myacls['GROUPS'][group]['PERMS'] + "\n" )
    fd.close()

def set_default_acl( filename=None, aclfile=None, dryrun=False, verbose=False ):
    cmd = MMPUTACL + '-d -i ' + aclfile + ' ' + filename
    if dryrun:
       print( cmd )
    else:
       if verbose:
          print( cmd )
       run_cmd( cmd )

def set_acl( filename=None, aclfile=None, dryrun=False, verbose=False ):
    cmd = MMPUTACL + '-i ' + aclfile + ' ' + filename
    if dryrun:
       print( cmd )
    else:
       if verbose:
          print( cmd )
       run_cmd( cmd )



if __name__ == '__main__':
   print("Get File ACL")
   a = mmacls( '/data/acl/a' )
   if a.filename:
      print("\nDump The Class Info:")
      a.dump_mmacl()
   else:
      print("File: %s does not exist." % ( a.fname ) )


