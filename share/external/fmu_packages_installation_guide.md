[![linting](https://github.com/equinor/fmu-drogon/actions/workflows/lint.yml/badge.svg)](https://github.com/equinor/fmu-drogon/actions/workflows/lint.yml)

# Install the FMU packages needed for FMU-Drogon

FMU-Drogon is the Equinor Open Source reservoir model.

This installation guide is three-folded:

1. Introduction to a basic installation for FMU on Linux
2. Install RMS from AspenTech (this is proprietary and licensed software) (exact procedure is work in progress)
3. Optional installation of the additional FMU-tools Resinsight and Webviz for visualization of results


# Introduction to a basic installation for FMU on Linux

In order to make Drogon run, a number of software packages are needed. This is only
tested on a Linux system, and RedHat 8 or CentOS 8 is recommended.

Most software are open source and can be downloaded and installed free of charge, but
beware the individual licences. An important exception is RMS which is proprietary. For
flow simulators, the open source reservoir simulator OPM Flow replaces the proprietary Eclipse software. 

The install procedure requires technical skills in Python, software compiling and OS
knowledge.

The install procedures in the coming pages are a proposal, so feel free to adapt to your
needs and knowledge.

##  Linux version and Python configuration

The software listed here and in the next pages are needed to make all workflows running.

Assume Linux: CentOS 8

Python version: Set python3 as default python in system (as root):

```sh
alternatives --install /usr/bin/python python /usr/bin/python2 50
alternatives --install /usr/bin/python python /usr/bin/python3 60
alternatives --config python
python --version
```

Note that some system tools like yum requires python2 as default, so you may need to run
``alternatives --config python`` for setting the specific session configuration.


## Install system components in a virtual environment

Python is a vital building block when running FMU.

It is strongly recommended to run the system python in a virtual environment:

```sh
python3 -m venv ~/venv/tutor
source ~/venv/tutor/bin/activate
pip install pip wheel setuptools setuptools_scm -U
```

## Install main FMU packages 

The following packages are required in order to run a full FMU Drogon run.

Continue inside the virtual env called tutor that was created above:
 
 ```sh
pip install ert xtgeo subscript fmu-config fmu-tools grid3d-maps
```

## Install reservoir simulator OPM Flow

Install the open source reservoir simulator OPM Flow according to the instructions here:

https://opm-project.org/?page_id=245

## Specific for sim2seis: Install FMU components related to sim2seis

The following packages are required in order to run the sim2seis workflow parts in the FMU Drogon workflows:

```sh
pip install si4ti
pip install seismic-forward 
```

## Run ERT

Use the drogon_design.ert example on ../ert/model

Set scratch folder in the ert file by editing the file and change the text "/scratch/fmu/" to "/tmp/".

Run the following command to start ERT:

```
ert gui drogon_design.ert
```


# Install RMS from AspenTech (this is proprietary and licensed software) (exact procedure is work in progress)

- A couple of tricks and issues are shown in the next subsections

- Assume for the rest of this guide that RMS is installed in /opt/roxar as
  ``/opt/roxar/rms/rms``
  This may be changed in runrms.yml if you have another installation-folder for RMS.

- Note that there is work in progress with simplifying the procedure for running FMU-Drogon outside of Equinor.

## Install RMS

This help guide, is based on that you have a RMS 14.2.2-installation.

- To install another version of RMS, simply replace references to `14.2.2` 
  with the RMS version of your choice
  - Note that RMS license is critical to be able to run RMS, 
    but about the RMS license, please contact AspenTech for details, help and for getting support assistance. 

## Install FMU components for RMS

Create this file from the bash-script-lines below :
(assuming that rms command is /opt/roxar/rms/rms)

$HOME/venv/tutor/bin/run_external

```sh
#!/usr/bin/env bash  
# wrapper script so running system python from RMS will work  
unset PYTHONPATH  
unset PYTHONUSERBASE  
unset LD_LIBRARY_PATH  
unset LD_LIBRARY64_PATH  

exec $@  
```  

Then copy the file here like this:

```sh
cp $HOME/venv/tutor/bin/run_external /opt/roxar/rms/run_external 
```

## Modify RMS startup

In /opt/roxar/rms * folder: rename “rms” to “rms_orig”, then make a new rms script containing this:

(*assume that rms command is /opt/roxar/rms/rms)

```sh
#!/bin/sh

export PATH=/opt/roxar/rms:$PATH

/opt/roxar/rms/rms_orig $@
```

## Install Python packages for RMS

In this example, the RMS Python packages will be installed automatically under $HOME/.roxar/python. There are better strategies if multiple users shall share the same libraries.

- Run roxenv script which is in the RMS installation folder tree, to activate RMS’s python:

```
/opt/roxar/rms/versions/14.2.2/bin/LINUX_64/roxenv
which python
/opt/roxar/rms/versions/14.2.2/linux-amd64-gcc_4_8-release/bin/python
```

- Now, given RMS’s python is active:

  - Install roxar_api_utils from https://github.com/RoxarAPI/roxar_api_utils in the user folder

  - Run these installation commands:

```
python -m pip install pip -U --user
python -m pip install xtgeo --user
python -m pip install wheel --user
python -m pip install setuptools_scm --user
python -m pip install fmu-config --user
python -m pip install fmu-tools --user
```  

## Run RMS for the first time

Run RMS for the virtual “tutor” environment

Now go to the folder “model” where the RMS project is present and type: 

```
rms
```

Run the workflow MAIN and see if it runs without issues!
       

# Optional installation of the additional FMU-tools Resinsight and Webviz for visualization of results

## Resinsight installation

- Resinsight is an Open Source tool that can be used to visualize results from Reservoir Simulation.

- Here is the Getting Started information for download and install Resinsight on Linux:

https://resinsight.org/getting-started/download-and-install/linux-installation/


##  WEBVIZ for Subsurface

Webviz-subsurface is an Open Source tool to visualize Subsurface data via a web-based user interface.

- Here is a demo of Webviz:

https://webviz-subsurface-example.azurewebsites.net

- See the GITHUB-repository for Webviz here:

https://github.com/equinor/webviz-subsurface

- Test data for webviz-subsurface:

https://github.com/equinor/webviz-subsurface-testdata

