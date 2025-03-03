#!/bin/sh
#
# Restores the project from the tar.gz file after a git update or clone
# Run the script from rms/model folder
#
# JRIV, 2022/2023
# rnyb, May 2024 - added version to runrms command

set -e

VERSION="14.2.2"

CURRENT="drogon.rms$VERSION"
GENERIC="drogon_git.rms$VERSION"

GIT_WF_RMS="restore_data_after_git_clone"
ZIPPED="drogon.tar.gz"

DTIME=$(date +%Y-%m-%d:%H:%M)

read -p "Current drogon project shall be: <$CURRENT>. Is this correct? (yes/no) " answer

if [ $answer == "no" ]; then
    echo "Please edit this script and update VERSION or CURRENT variable."
    exit
else
    echo "You did not answer 'no'; will continue in 5 seconds...(hence CTRL-C if PANIC)"
    sleep 5
fi

if [[ $(pwd) == *"drogon/resmod/ff/dev"* ]]; then
    echo "--Exiting-- Restore in drogon/resmod/ff/dev folder is blocked."
    exit
fi

if [ -d "$CURRENT" ]; then
    echo "Found project $CURRENT, OK... will make backup in /tmp/"
    echo "Make a restore backup copy of the current $CURRENT project..."

    BACKUPNAME="/tmp/${CURRENT}.backup_restore.${DTIME}"

    echo "Copy project from $CURRENT to backup: $BACKUPNAME ..."
    /bin/cp -rp $CURRENT $BACKUPNAME
    sleep 2  # just to secure that copy is settled...
else
    echo "No existing project $CURRENT, will continue without any attempt for backup..."
fi


export "PROJECT_GIT_RESTORE"=1  # applied in RMS to detect restore mode for APS grid

if [ -r "$CURRENT/.master" ]; then
     if [ -r $ZIPPED ]; then
         if [ "$CURRENT/.master" -nt $ZIPPED ]; then
             echo "The current project $CURRENT is newer than $ZIPPED. STOP!"
             exit
         else
             echo "OK, the $ZIPPED is newer than $CURRENT"
         fi
     fi
fi

if [ -r "$ZIPPED" ]; then
    echo "Uncompress $ZIPPED..."
    tar xzf $ZIPPED
else
    echo "No zipped file $ZIPPED found. STOP!"
    exit
fi

if [ -d "$GENERIC" ]; then

    if [ -z "$KOMODO_RELEASE" ]; then
        echo "Komodo is not enabled. STOP!"
        exit 1
    fi

    RESTORELOG="/tmp/drogon_git_restore_${DTIME}.log"

    echo "Next run the workflow in RMS that restores data..."
    echo
    echo "**** This may take some time, so take a coffee or work with P@E! :-P ****"
    echo "**** If you take CTRL-C, processes may still run in the background! ****"
    echo "**** CHECK THIS AFTERWARDS! $RESTORELOG ****"
    echo

    sleep 3
    set +e  # eclrun.bash can trigger exit on string comparisons
    source /prog/res/ecl/script/eclrun.bash #!/bin/sh -> /bin/bash
    set -e
    runrms --version $VERSION  $GENERIC --batch $GIT_WF_RMS > $RESTORELOG 2>&1
    echo "RMS restore is now finished!"
else
    echo "No $GENERIC present. STOP!"
    exit
fi

if [ -d "$CURRENT" ]; then
    echo "The backup copy is present, will now make a new $CURRENT..."

    /bin/rm -rf $CURRENT
    echo "Removed the original project... (if you need backup, check /tmp folder)"
fi
/bin/mv $GENERIC $CURRENT

# Auto-remove some files if not in dev folder
if ! [[ $(pwd) == *"dev"* ]]; then
    /bin/rm -rf $ZIPPED  # delete tarball after successful restore
    /bin/rm -f *.log   # delete log files after successful restore
fi

echo "That is all, project $CURRENT is now restored and ready!"
