#!/bin/bash
#
# Make yml and yml.tmpl files for rate scaling
#--------------------------------------------------

RATE_SCALING_CONFIG="../../fmuconfig/input/drogon_rate_scaling_config.yml"  # well rate scaling config
RATE_SCALING_ROOTNAME="rate_scaling"
OUTFOLDER="../../fmuconfig/output"


#--------------------------------------------------
# Delete previous versions
rm -f ${OUTFOLDER}/${RATE_SCALING_ROOTNAME}.*   # be careful with this!


#--------------------------------------------------
# Run command for creating rate scaling yml and yml.tmpl files
fmuconfig $RATE_SCALING_CONFIG --rootname $RATE_SCALING_ROOTNAME --mode yml --destination $OUTFOLDER   --template $OUTFOLDER

#--------------------------------------------------
