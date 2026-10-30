#!/bin/bash
#
# Runs a compress in RMS first and saves to a generic name.
#
# Run this script from rms/model folder as sh ../scripts/<this_script>
#
# JRIV, dec. 2022, last update mar 2023
# rnyb, May 2024 - added version to runrms command
# rnyb, Dec 2025 - rms version 15.0.1.0

set -eu

VERSION="15.0.1.0"

CURRENT="drogon.rms$VERSION"
GENERIC="drogon_git.rms$VERSION"
GIT_WF_RMS="minimize_data_for_git"
TARGET="drogon.tar.gz"
PYTHON_BACKUP="backup_pythoncomp"  # potentially from rename_rms_scripts.py

if [ -z "${KOMODO_RELEASE:-}" ]; then
    echo "Komodo is not enabled. STOP!"
    exit 1
fi

if [ -d "$CURRENT" ]; then
    echo "Found project $CURRENT, OK..."
else
    echo "No project: $CURRENT; edit the VERSION variable in this script!"
    exit 1
fi

if [ -e "$CURRENT/project_lock_file" ]; then
    echo "A lockfile is present. Please close the project and retry! STOP"
    exit 1
fi

rm -rf "${PYTHON_BACKUP:?}"

# Make a copy of the project to a backup tagged with datetime
DTIME=$(date +%Y-%m-%d_%H-%M-%S)
BACKUPNAME="/tmp/${CURRENT}.backup.${DTIME}"
echo "Copy project from $CURRENT to backup: $BACKUPNAME ..."
cp -rp "$CURRENT" "$BACKUPNAME"

# Run the RMS git workflow
rm -rf "${GENERIC:?}"
echo "Run the workflow in RMS that minimizes data..."
runrms --version "$VERSION" "$CURRENT" --batch "$GIT_WF_RMS"

if [ ! -d "$GENERIC" ]; then
    echo "No git output as $GENERIC! STOP!"
    exit 1
fi

echo "Found git project $GENERIC, OK..."
rm -f "${TARGET:?}"  # remove any stale target
rename_rms_scripts --verbose "$GENERIC"
tar czf "$TARGET" "$GENERIC"

rm -rf "${GENERIC:?}"

echo "Project is compressed as $TARGET and the generic folder is removed."
echo "The actual RMS project $CURRENT is untouched; backup is in $BACKUPNAME."
