#!/bin/bash
#
# rnyb Feb 19, create file containing ert config name (including full path) and time it was run
#              run as ert pre_simulation or pre_experiment hook workflow job 
#
# rnyb, Sep 19, added user name to output
# rnyb, Jun 22, added host and komodo info
# alifb, Jan 24, added ERT run mode      
#-----------------------------------------------------------------------

configpath=$1
outfile=$2

#append new line for every time ert is run for current casedir (keep history)
echo 'Write ert config file info to ' $outfile
echo '---------------------------------' >> $outfile
echo Run by $USER, $(date): >> $outfile
echo $configpath >> $outfile
echo "ERT running on host : $HOSTNAME" >> $outfile
echo "Komodo release      : $KOMODO_RELEASE" >> $outfile
echo "ERT run mode        : $_ERT_SIMULATION_MODE" >> $outfile
