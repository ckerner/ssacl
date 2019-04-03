#!/bin/bash

#set -x

GPFSDEV=$1
if [ "x${GPFSDEV}" == "x" ] ; then
   PROG=`basename $0`
   cat <<EOHELP

   Usage: ${PROG} [GPFS DEVICE] 
EOHELP
   exit 1
fi

QUIET=1
PID=$$

MYDATE=`date +"%Y%m%d"`
ACLDIR="/PATHTO/admin/acl"
BKUPDIR="${ACLDIR}/backups"
CURRENT="${ACLDIR}/acls.${GPFSDEV}_${MYDATE}"
WORKDIR="${ACLDIR}/tmp/acls.${PID}"
OUTPUT="${WORKDIR}/list.all-files"
POLICY_FILE="${WORKDIR}/policy.in"
LOGFILE="${WORKDIR}/policy.log"

mkdir -p ${WORKDIR} &>/dev/null
mkdir -p ${BKUPDIR} &>/dev/null

cat <<EOPOLICY >${POLICY_FILE}
RULE 'listall' LIST 'all-files' DIRECTORIES_PLUS
SHOW ( varchar(user_id) || '  ' || varchar(group_id) || '  ' || mode || '  ' || misc_attributes )
WHERE MISC_ATTRIBUTES like '%+%'
EOPOLICY


if [ ${QUIET} -eq 1 ] ; then
   /usr/lpp/mmfs/bin/mmapplypolicy ${GPFSDEV} -f ${WORKDIR} -g ${WORKDIR} -N coreio -P ${POLICY_FILE} -I defer &>${LOGFILE}
else
   /usr/lpp/mmfs/bin/mmapplypolicy ${GPFSDEV} -f ${WORKDIR} -g ${WORKDIR} -N coreio -P ${POLICY_FILE} -I defer
fi

cp -pf ${OUTPUT} ${CURRENT}
RC=$?
if [ ${RC} -eq 0 ] ; then
   rm -Rf ${WORKDIR}
fi

# OK, we have the list of files, lets go to work
MYDIR=`dirname $0`

${MYDIR}/backup_acls.py -f ${CURRENT} -v &>"${BKUPDIR}/${GPFSDEV}_${MYDATE}"

