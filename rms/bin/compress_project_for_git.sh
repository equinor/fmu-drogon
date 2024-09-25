#!/bin/sh
#
# Runs a compress in RMS first. The project is in that workflow saved to
# a generic name, due to a bug that creates large volvizcache files
# (the save_as() fix this.
#
# Run the script from rms/model folder
#
# JRIV, dec. 2022, last update mar 2023
# rnyb, May 2024 - added version to runrms command

set -e

VERSION="14.2.2"

CURRENT="drogon.rms$VERSION"
GENERIC="drogon_git.rms$VERSION"

GIT_WF_RMS="minimize_data_for_git"
TARGET="drogon.tar.gz"

PYTHON_BACKUP="backup_pythoncomp"  # potentially from rename_rms_scripts.py

if [ -d "$CURRENT" ]; then
    echo "Found project $CURRENT, OK..."
else
    echo "No project: $CURRENT; edit the VERSION variable in this script!"
    exit
fi

if [ -r "$CURRENT/project_lock_file" ]; then
    echo "A lockfile is present. Please close the project and retry! STOP"
    exit
fi

if [ -d $PYTHON_BACKUP ]; then
    /bin/rm -fr $PYTHON_BACKUP
fi

if [ -z "$KOMODO_RELEASE" ]; then
    echo "Komodo is not enabled. STOP!"
    exit 1
fi

# next make a copy of the project to a backup tagged with datetime
DTIME=$(date +%Y-%m-%d:%H:%M)
BACKUPNAME="/tmp/${CURRENT}.backup.${DTIME}"
echo "Copy project from $CURRENT to backup on /tmp/: $BACKUPNAME ..."
/bin/cp -rp $CURRENT $BACKUPNAME
sleep 2  # just to secure that copy is settled...

# now run the git work flow
rm -rf $GENERIC
echo "Run the workflow in RMS that minimizes data..."
runrms --version $VERSION  $CURRENT --batch $GIT_WF_RMS

if [ -d $GENERIC ]; then
    echo "The git project is found... OK"
    # clean-up the RMS Python scripts
    echo "First clean up python naming under pythoncomp..."
    rename_rms_scripts --verbose $GENERIC
    echo "Compress project..."
    tar czf $TARGET $GENERIC
    echo "Project is now compressed as $TARGET"
else
    "No git output as $GENERIC! STOP!"
    exit
fi

echo "That is all, project is compressed as $GENERIC inside $TARGET, and ready!"
rm -rf $GENERIC
echo "The generic RMS project is now packed, and the generic is removed."
echo "The actual RMS project $CURRENT shall be untouched, but still backups in /tmp/"
