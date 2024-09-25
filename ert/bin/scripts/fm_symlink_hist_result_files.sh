#!/bin/bash
#---------------------------------------------------
# Shell wrapper script to make symlinks to hist case share/result files. This is a
# convenience script to make hist results available together with pred case results when
# using RMS-covisualization and sim2seis.
#------------------
# rnyb, Sept 22
#---------------------------------------------------


DIR_FROM=$1  # full path to directory containing files to link
DIR_TO=$2    # full path to directory to create symlinks in
             # DIR_TO may also be given as relative to ert runpath

echo "Create symlinks to all files in $DIR_FROM in $DIR_TO"
for file in "$DIR_FROM"/*;
do
	filename=$(basename "$file")
	# echo "$file  $DIR_TO/$filename"
	ln -s "$file" "$DIR_TO/$filename"
done

echo "Done"
