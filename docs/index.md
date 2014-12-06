# Introduction

Instrap is a set of utilities for automating the manual steps
required to set up an instack installation via source with
Tuskar.

This means we automate the steps described on:

- [instack-undercloud via source](https://github.com/agroup/instack-undercloud/blob/master/README-source.md)
- [Using Tuskar and Tuskar UI with instack](https://wiki.openstack.org/wiki/Tuskar/Instack)


## Setup

I'd recommend doing this within a virtualenv, but that is
optional. Without it you may need sudo for some of the following
commands.

    git clone git@github.com:d0ugal/instrap.git
    cd instrap
    pip install -r requirements.txt

Then to view the commands run `fab -l` from within the directory.
