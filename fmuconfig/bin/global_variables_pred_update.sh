#!/bin/bash
#
# Create global variables files for use with prediction cases
#
# Files created will be
#    ../../fmuconfig/output/global_variables_pred.yml
#    ../../fmuconfig/output/global_variables_pred.yml.tmpl
#
#=======================================================================================

MASTER="../../fmuconfig/input/global_master_config_pred.yml"  # prediction spesific variables
OUTFOLDER="../../fmuconfig/output"                            # location of result files
ROOTNAME="global_variables_pred"                              # root name of result files

rm -f ${OUTFOLDER}/${ROOTNAME}.*   # be careful with this!

# run command for creating YAML version (+ ert tmpl version; yml.tmpl)
fmuconfig $MASTER --rootname $ROOTNAME --mode yml --destination $OUTFOLDER \
          --template $OUTFOLDER

# # run command for creating IPL version if needed (+ ert tmpl version; ipl.tmpl)
# fmuconfig $MASTER --rootname $ROOTNAME --mode ipl --destination $OUTFOLDER \
#           --template $OUTFOLDER --tool rms
