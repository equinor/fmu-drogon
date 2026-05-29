# Drogon FMU model

Drogon is a synthetic reservoir model developed and maintained by Equinor. It includes a
complete FMU (Fast Model Update) set-up.

# Drogon FMU model on github

Files and folders for Drogon FMU.

This GitHub version is a minimized version that requires a restoring workflow to be run
after a git clone (Equinor). As an alternative for externals, one can use a bundle that
includes a restored state of Drogon, located in share/external folder.

As the RMS project is stored as a large binary file we may need to restrict how often we
push it, as the full size of it will stack up each time. This has the downside that the
latest commit(s) may have inconsistencies. For tagged versions however, RMS should
always be at par with all other files.

Git LFS is used for storing the large binary files, so ensure you have it installed
before cloning/pushing/pulling (one time install locally per user):

``` shell
git lfs install
```

## Note

Since RMS is not fully integrated (we upload a zipped and archived version), PRs
involving RMS should be clarified with admins upfront, otherwise they are likely to be
rejected.


Even if one does not have access to fully restore the project, cloning it could still be
a useful way of accessing model files, scripts, workflows, etc.


## License

This work is dual-licensed under CC-BY-SA-4.0 and GPL-3.0 (or any later version). Please
see the files LICENSE-CCBYSA and LICENSE-GPLV3 for full details.

Data and text files in this work are licensed under the
[Creative Commons Attribution-ShareAlike 4.0 International License][cc-by-sa].

Code (mostly Python) in this work is licensed under the
[GNU General Public License Version 3][gpl-v3].


[![CC BY-SA 4.0][cc-by-sa-shield]][cc-by-sa]
[![GPL-V3][gpl-v3-shield]][gpl-v3]


[cc-by-sa]: https://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-shield]: https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg

[gpl-v3]: https://www.gnu.org/licenses/gpl-3.0.en.html
[gpl-v3-shield]: https://img.shields.io/badge/License-GPLv3-blue.svg
