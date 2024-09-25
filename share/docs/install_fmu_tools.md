[![linting](https://github.com/equinor/fmu-drogon/actions/workflows/lint.yml/badge.svg)](https://github.com/equinor/fmu-drogon/actions/workflows/lint.yml)

# Install Drogon

The Equinor Open Source reservoir model


## Introduction

In order to make Drogon run, a number of software packages are needed. This is only
tested on a Linux system, and RedHat 8 or CentOS 8 is recommended.

Most software are open source and can be downloaded and installed free of charge, but
beware the individual licences. An important exception is RMS which is proprietary. For
flow simulators, the open source OPM-flow replaces the proprietary Eclipse software. 

The install procedure requires technical skills in python, software compiling and OS
knowledge.

The install procedures in the coming pages is a proposal, so feel free to adapt to your
needs and knowledge.

##  Installation

In order to make Drogon run, a number of software packages are needed. Software listed
here and in the next pages are needed to make all workflows running.

Assume Linux: Redhat-8

Optional: Set python3 as default python in system (as root):

- alternatives --install /usr/bin/python python /usr/bin/python2 50
- alternatives --install /usr/bin/python python /usr/bin/python3 60
- alternatives --config python
- python --version

Note that some system tools like yum requires python2 as default, so you may need to run
alternatives --config python for a session


Install RMS from AspenTech (this is propriatary and licensed software)

- A couple of trick and issues on the next page

- Assume for the rest of this guide that that rms is installed in /opt/roxar as
  /opt/roxar/rms/rms


## Install RMS

In this help guide, we will be installing RMS 14.2.2.

- To install another version of RMS, simply replace references to «14.2.2» with the RMS
  version of your choice
  - The flexlm install which is bundled with RMS does not work out of the box; you may
    need to use lmgrd and geomatic.lic from a newer version
  - The lmgrd daemon must run in order to RMS to work
  - RMS is not Equinor responsibility, so please visit AspenTech for detail, help and
    support

## Install system components in a virtual environment

Python is an vital building block when running FMU.

It is strongly recommended to run the system python in a virtual environment:

- python3 -m venv ~/venv/tutor
- source ~/venv/tutor/bin/activate
- pip install pip wheel setuptools setuptools_scm -U

## Install system components (2)

The following packages are required in order to run a full FMU Drogon run.

Continue inside the virtual env called tutor:

- which pip
  - ~/venv/tutor/bin/pip
- pip install xtgeo
- pip install ert
- pip install git+https://github.com/equinor/fmu-config
- pip install git+https://github.com/equinor/subscript
- pip install git+https://github.com/equinor/grid3d-maps

- Install opm according to instructions https://opm-project.org/?page_id=245



## Install system components (3)

The following packages are required in order to run a full FMU Drogon run.

- Install si4ti according to instructions on github pages: https://github.com/equinor/si4ti
- Install seismic forward according to instructions: TODO!


## Install system components (4)

Add this file in two locations: $HOME/venv/tutor/bin/run_external  and /opt/roxar/rms *

(*assume that rms command is /opt/roxar/rms/rms)

>\#!/usr/bin/env bash  
>\# wrapper script so running system python from RMS will work  
>unset PYTHONPATH  
>unset PYTHONUSERBASE  
>unset LD_LIBRARY_PATH  
>unset LD_LIBRARY64_PATH  
>
>exec $@  
  

## Modify RMS startup

In /opt/roxar/rms * folder: mv “rms” to “rms_orig”, then make a new rms script

(*assume that rms command is /opt/roxar/rms/rms)

>\#!/bin/sh
>
>export PATH=/opt/roxar/rms:$PATH
>
>/opt/roxar/rms/rms_orig $@'


## Install python packages for RMS

In this example, the RMS python packages will come automatically under $HOME/.roxar/python. There are better strategies if multiple users shall share the same libraries.

- Run roxenv script which is in the RMS install, to activate RMS’s python

  - /opt/roxar/rms/versions/14.2.2/bin/LINUX_64/roxenv
  - which python
    - /opt/roxar/rms/versions/14.2.2/linux-amd64-gcc_4_8-release/bin/python'

- Now, given RMS’s python is active:

  - python -m pip install pip -U --user
  - python -m pip install xtgeo --user
  - python -m pip install wheel --user
  - python -m pip install setuptools_scm --user
  - python -m pip install git+https://github.com/equinor/fmu-config --user
  - Install roxar_api_utils from https://github.com/RoxarAPI/roxar_api_utils in the user folder


## Run RMS for the first time

Run RMS for the virtual “tutor” environment

Now go to the folder “model” where the RMS project is present and type: rms

Run the workflow MAIN and see if it runs without issues!


## Run ERT

Use drogon_ahm.ert example on ../ert/model

Set scratch folder in the ert file by editing the file with /scratch/fmu/… to /tmp/

ert gui drogon_ahm.ert

Issues:

- Change job FM_OPM so it points to /usr/bin/flow

Currently:

- RMS runs
- OPM runs

Stops at GRID_HC THICKNESS (probably a minor issue)
       


