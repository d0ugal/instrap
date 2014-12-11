# Introduction

Instrap is a set of utilities for automating the manual steps
required to set up an instack installation via source with
Tuskar.

This means we automate the steps described on:

- [instack-undercloud via source](https://github.com/agroup
  /instack-undercloud/blob/master/README-source.md)
- [Using Tuskar and Tuskar UI with
  instack](https://wiki.openstack.org/wiki/Tuskar/Instack)


## Setup

I'd recommend doing this within a virtualenv, but that is
optional. Without it you may need sudo for some of the following
commands.

    git clone git@github.com:d0ugal/instrap.git cd instrap pip
    install -r requirements.txt

Then to view the commands run `fab -l` from within the directory.


## Running Instrap

To setup instack with Instrap, the commands need to be run in a
specific order. To execute these commands you will need to invoke
them as `fab -H $HOST $COMMAND`

### 1. fab -H $HOST host

This command does some basic host setup.

- install tmux and git
- create a stack user with password-less sudo
- Checkout TripleO and install dependencies
- Start the download of the Juno images used later for the
  undercloud.

### 2. fab -H $HOST undercloud_create

Creates the instack virt setup, four virtual machines to emulate
a baremetal setup.


### 3. fab -H $HOST undercloud_setup

Before running this command, step 2 needs to have finished. To
verify this after you ssh into the host as the stack user, view
the tmux session with `tmux attach -t instack` and if it has
finished you will see an IP address at the bottom. Something
like:

    instack vm IP address is 192.168.122.53

If that all looks good, then go ahead and run the command. To
view the process connect to the host and attach to the tmux
session named `undercloud`
