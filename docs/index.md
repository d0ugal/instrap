# Instrap - Bootstrapping Instack.

Instrap is a set of utilities for automating the manual steps
required to set up an instack installation via source with
Tuskar.

This means we will automate the steps described on:

- [instack-undercloud via source](https://github.com/agroup
  /instack-undercloud/blob/master/README-source.md)
- [Using Tuskar and Tuskar UI with
  instack](https://wiki.openstack.org/wiki/Tuskar/Instack)

__**NOTE: At the moment, only the Instack undercloud steps are
implemented.**__


## Setup

I'd recommend doing this within a virtualenv, but that is
optional. Without it you may need sudo for the `pip install`.

```bash
git clone git@github.com:d0ugal/instrap.git
cd instrap
pip install -r requirements.txt
```

Then to view the commands run `fab -l` from within the directory.
The commands are explained below in some detail in a suggested
install flow.


## Running Instrap

To setup instack with Instrap, the commands need to be run in a
specific order. To execute these commands you will need to invoke
them as `fab -H $HOST $COMMAND`

### 1. fab -H $HOST host.setup

This command performs initial setup of the host machine.

- install tmux and git
- create a stack user with password-less sudo
- Checkout TripleO and install dependencies in a tmux session
  named `tripleo`.
- Start the download of the OpenStack Juno images used later for
  the undercloud in a tmux session named `image-dl`.

### 2. fab -H $HOST undercloud.create

Create the instack virt setup, this essentially just calls the
instack command `instack-virt-setup` in a tmux session named
`instack`.

It will then ssh into the undercloud when it is created and
finish the setup. This happens in the tmux session named
`undercloud`.


## Utility Commands


### fab -H $HOST host.list_images

Display a list of the images stored on the host.


### fab -H $HOST host.tmux_list

List all the active tmux sessions on the host machine.


### fab -H $HOST host,tmux_buffer:$SESSION

Display the current buffer for a tmux session - useful for
viewing progress of a command.


### fab -H $HOST host.virsh_list

List all the VM's running on the host in the instack virt setup.


### fab -H $HOST underloud.destroy

Destroy the current undercloud, to re-create it you would be back
at step 2.
