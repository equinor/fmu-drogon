#!/bin/bash
#
# Restores the project from the tar.gz file after a git update or clone
# Run the script from rms/model folder
#
# JRIV, 2022/2023
# rnyb, May 2024 - added version to runrms command
# rnyb, Dec 2025 - rms version 15.0.1.0

set -e

VERSION="15.0.1.0"

CURRENT="drogon.rms$VERSION"
GENERIC="drogon_git.rms$VERSION"

GIT_WF_RMS="restore_data_after_git_clone"
ZIPPED="drogon.tar.gz"

DTIME=$(date +%Y-%m-%d_%H_%M)

read -r -p "Current drogon project shall be: <$CURRENT>. Is this correct? (yes/no) " answer

case "$answer" in
    yes|YES|y|Y)
        echo "Continuing in 5 seconds... (CTRL-C if PANIC)"
        sleep 5
        ;;
    *)
        echo "Aborting. Please edit this script and update the VERSION variable."
        exit 1
        ;;
esac

if [[ $(pwd) == *"drogon/resmod/ff/dev"* ]]; then
    echo "--Exiting-- Restore in drogon/resmod/ff/dev folder is blocked."
    exit 1
fi

if [ -z "${KOMODO_RELEASE:-}" ]; then
    echo "Komodo is not enabled. STOP!"
    exit 1
fi

if [ ! -r "$ZIPPED" ]; then
    echo "No zipped file $ZIPPED found. STOP!"
    exit 1
fi


if [ -r "$CURRENT/.master" ]; then
    if [ "$CURRENT/.master" -nt "$ZIPPED" ]; then
        echo "The current project $CURRENT is newer than $ZIPPED. STOP!"
        exit 1
    else
        echo "OK, the $ZIPPED is newer than $CURRENT"
    fi
fi

if [ -d "$CURRENT" ]; then
    echo "Found project $CURRENT, OK... will make backup in /tmp/"
    echo "Make a restore backup copy of the current $CURRENT project..."

    BACKUPNAME="/tmp/${CURRENT}.backup_restore.${DTIME}"

    echo "Copy project from $CURRENT to backup: $BACKUPNAME ..."
    /bin/cp -rp "$CURRENT" "$BACKUPNAME"
else
    echo "No existing project $CURRENT, will continue without any attempt for backup..."
fi


export PROJECT_GIT_RESTORE=1  # applied in RMS to detect restore mode for APS grid


if [ -e "$GENERIC" ]; then
    echo "Removing stale $GENERIC from an earlier run..."
    /bin/rm -rf "${GENERIC:?}"
fi

echo "Uncompress $ZIPPED..."
tar xzf "$ZIPPED"

if [ -d "$GENERIC" ]; then

    # temp fix for RMS15.0 bug - remove problematic file before restoring
    BAD_FILE="$GENERIC/gridmodels/simgrid/connections/realisation"
    if [ -e "$BAD_FILE" ]; then
        echo "Applying workaround for RMS 15.0 bug: removing $BAD_FILE"
        rm -f "$BAD_FILE"
    fi

    RESTORELOG="/tmp/drogon_git_restore_${DTIME}.log"

    echo "Next run the workflow in RMS that restores data..."
    echo "---- This may take some time ..."
    echo "---- If you take CTRL-C, processes may still run in the background!"
    echo "---- CHECK THIS AFTERWARDS! $RESTORELOG"
    echo

    set +e  # eclrun.bash can trigger exit on string comparisons
    source /prog/res/ecl/script/eclrun.bash
    set -e

    if ! runrms --version "$VERSION" "$GENERIC" --batch "$GIT_WF_RMS" > "$RESTORELOG" 2>&1; then
        echo "RMS restore FAILED. See $RESTORELOG. Existing $CURRENT is untouched. STOP!"
        exit 1
    fi

    echo "RMS restore is now finished!"
else
    echo "$GENERIC not found after extracting $ZIPPED. STOP!"
    exit 1
fi

if [ -d "$CURRENT" ]; then
    echo "Replacing existing $CURRENT (backup: ${BACKUPNAME:-none})..."
    if ! /bin/rm -rf "${CURRENT:?}"; then
        echo "Could not remove $CURRENT completely. Is the project open in RMS?"
        echo "Close RMS, then run: rm -rf $CURRENT; mv $GENERIC $CURRENT"
        exit 1
    fi
    echo "Removed the original project... (if you need backup, check /tmp folder)"
fi

/bin/mv "$GENERIC" "$CURRENT"

/bin/rm -f "${ZIPPED:?}"  # delete tarball after successful restore
/bin/rm -f ./*.log        # delete RMS log files after successful restore

echo "Done, project $CURRENT is now restored and ready! (backup: ${BACKUPNAME:-none})"
