#!/bin/bash
#
# Run the global configuration for RMS, both making IPL (not in Drogon)...
# and YAML versions from a common global config
#
#--------------------------------------------------

MASTER="../../fmuconfig/input/global_master_config.yml"    # global variables config
OUTFOLDER="../../fmuconfig/output"                         # location of result files
ROOTNAME="global_variables"                                # root name of result files

#--------------------------------------------------
# Delete all previous versions
rm -f ${OUTFOLDER}/${ROOTNAME}.*   # be careful with this!


#--------------------------------------------------
# run command for creating YAML version (+ ert tmpl version; yml.tmpl)
fmuconfig $MASTER --rootname $ROOTNAME --mode yml --destination $OUTFOLDER \
          --template $OUTFOLDER

# run command for creating IPL version if needed (+ ert tmpl version; ipl.tmpl)
fmuconfig $MASTER --rootname $ROOTNAME --mode ipl --destination $OUTFOLDER \
          --template $OUTFOLDER --tool rms

